import datetime
import enum
import re
import sys
from typing import (
    Any, Generic, Optional, Type, TypeVar, Literal
)

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import UUID4
from sqlalchemy import select, or_, func
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.relationships import RelationshipProperty
from starlette import status

from config.logger import log
from db.base_class import APIBase
from db.session import engine
from domains.appraisal.models.appraisal import Appraisal
from domains.appraisal.models.appraisal_comment import AppraisalComment, appraisal_submission_comments
from domains.appraisal.models.appraisal_input import AppraisalInput
from domains.appraisal.models.appraisal_submission import AppraisalSubmission
from domains.appraisal.models.appraisal_template import AppraisalTemplate
from domains.appraisal.models.department_group import DepartmentGroup
from domains.auth.models.role_permissions import Role, role_permissions, Permission
from domains.organization.models import Organization
from domains.organization.models.form_template import FormFieldTemplate
from domains.organization.models.organization_branch import OrganizationBranch
from domains.organization.models.organization_settings import OrganizationSettings
from domains.staff.models.department import Department
from domains.staff.models.staff import Staff
from utils.constants import SORT_STR_X, Q_STR_X, convert_datetimes_recursive
from utils.exceptions import raise_exc

ModelType = TypeVar("ModelType", bound=APIBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def str_to_datetime(value: str) -> datetime.datetime:
    # Convert string to datetime. Implement as needed for your project.
    return datetime.datetime.fromisoformat(value)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations on database models.

    Provides common database operations with error handling and type safety.

    Type Parameters:
        ModelType: The SQLAlchemy model type
        CreateSchemaType: Pydantic model for creation operations
        UpdateSchemaType: Pydantic model for update operations
    """

    def __init__(self, model: Type[ModelType], extra_models: list = None, *args, **kwargs):
        """
        Initialize the repository with a specific model.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model
        self.extra_models = extra_models

    async def get_by_id(
            self, db: AsyncSession, *,
            id: Any,
    ) -> Optional[ModelType]:

        if id is None:
            return None
        existing_org = await db.execute(select(self.model).where(self.model.id == id))
        existing_org = existing_org.scalars().first()

        if not existing_org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )

        return existing_org

    async def create(self, db: AsyncSession, *, data: CreateSchemaType, unique_fields: list) -> ModelType:
        """
        Create a new record.
        Checks multiple unique fields to ensure their values do not already exist.
        Converts timezone-aware datetime values to naive datetimes.
        """
        try:
            if not data:
                return None

            # Get input data and convert any timezone-aware datetime to naive UTC
            obj_in_data = convert_datetimes_recursive(data.model_dump())

            # Check each unique field for duplicates.
            for field in unique_fields:
                if field in obj_in_data and obj_in_data[field]:
                    query = select(self.model).where(getattr(self.model, field) == obj_in_data[field])
                    result = await db.execute(query)
                    if result.scalars().first():
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"'{field}' for {obj_in_data[field]} already exists"
                        )

            # Create and commit the new record.
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail="{}".format(sys.exc_info()[1]))

    async def create_for_tenant(self, db: AsyncSession, *, data: CreateSchemaType, organization_id: UUID4,
                                unique_fields: list) -> ModelType:
        """
        Create a new record in the tenant-specific schema.
        Checks multiple unique fields ("name", "org_email", "domain_name")
        to ensure their values do not already exist.
        """
        try:
            if not data:
                return None

            org_result = await db.execute(select(Organization).where(Organization.id == organization_id))
            organization_obj = org_result.scalars().first()
            if not organization_obj:
                raise HTTPException(status_code=404, detail="Organization not found")
            schema = organization_obj.domain_name

            self.model.__table__.schema = schema
            await db.execute(text(f'SET search_path TO "{schema}"'))

            obj_in_data = data.model_dump()

            for field in unique_fields:
                if field in obj_in_data and obj_in_data[field]:
                    query = select(self.model).where(getattr(self.model, field) == obj_in_data[field])
                    result = await db.execute(query)
                    if result.scalars().first():
                        raise HTTPException(
                            status_code=400,
                            detail=f"'{field}' for {obj_in_data[field]} already exists"
                        )

            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail="{}".format(sys.exc_info()[1]))

    async def update(
            self,
            db: AsyncSession,
            *,
            id: Any,
            data: UpdateSchemaType,
            unique_fields: list
    ) -> Optional[ModelType]:
        """Update an existing record using tenant schema.
        
        This function sets the search_path based on the organization_id,
        then checks that new unique field values do not already exist.
        """
        existing_obj = await self.get_by_id(db, id=id)
        if not existing_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )

        update_data = data.model_dump(exclude_unset=True)

        # Check for duplicates for each unique field.
        for field, new_value in update_data.items():
            if field in unique_fields and new_value != getattr(existing_obj, field):
                query = select(self.model).where(
                    getattr(self.model, field) == new_value,
                    self.model.id != id
                )
                result = await db.execute(query)
                if result.scalars().first():
                    raise HTTPException(
                        status_code=400,
                        detail=f"'{field}' for '{new_value}' already exists"
                    )

        for field, value in update_data.items():
            setattr(existing_obj, field, value)

        try:
            db.add(existing_obj)
            await db.commit()
            await db.refresh(existing_obj)
            return existing_obj
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail="Integrity error")

    async def update_for_tenant(
            self,
            db: AsyncSession,
            *,
            id: Any,
            data: UpdateSchemaType,
            organization_id: UUID4,
            unique_fields: list
    ) -> Optional[ModelType]:
        """Update an existing record using tenant schema.
        
        This function sets the search_path based on the organization_id,
        then checks that new unique field values do not already exist.
        """
        existing_obj = await self.get_by_id(db, id=id)
        if not existing_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )

        org_result = await db.execute(select(Organization).where(Organization.id == organization_id))
        organization_obj = org_result.scalars().first()
        if not organization_obj:
            raise HTTPException(status_code=404, detail="Organization not found")
        schema = organization_obj.domain_name

        # Set the model's schema and update the search_path.
        self.model.__table__.schema = schema
        await db.execute(text(f'SET search_path TO "{schema}"'))

        update_data = data.model_dump(exclude_unset=True)

        # Check for duplicates for each unique field.
        for field, new_value in update_data.items():
            if field in unique_fields and new_value != getattr(existing_obj, field):
                query = select(self.model).where(
                    getattr(self.model, field) == new_value,
                    self.model.id != id
                )
                result = await db.execute(query)
                if result.scalars().first():
                    raise HTTPException(
                        status_code=400,
                        detail=f"'{field}' for '{new_value}' already exists"
                    )

        for field, value in update_data.items():
            setattr(existing_obj, field, value)

        try:
            db.add(existing_obj)
            await db.commit()
            await db.refresh(existing_obj)
            return existing_obj
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail="Integrity error")

    async def soft_delete(self, db: AsyncSession, *, id: Any) -> None:
        """Soft-delete a record by its ID by setting is_deleted to True, is_active to False, and deleted_at to current time."""
        existing_obj = await self.get_by_id(db, id=id)
        if not existing_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )

        try:
            existing_obj.is_deleted = True
            existing_obj.is_active = False
            existing_obj.deleted_at = datetime.datetime.utcnow()

            # Mark the object as changed
            db.add(existing_obj)
            await db.commit()
        except Exception as ex:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(ex))

    async def soft_delete_for_tenant(self, db: AsyncSession, *, id: Any, organization_id: UUID4) -> None:
        """Soft-delete a record by its ID using the tenant schema.
        
        Sets is_deleted to True, is_active to False, and deleted_at to the current time.
        The tenant schema is determined using organization_id.
        """
        org_result = await db.execute(select(Organization).where(Organization.id == organization_id))
        organization_obj = org_result.scalars().first()
        if not organization_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        schema = organization_obj.domain_name

        self.model.__table__.schema = schema
        await db.execute(text(f'SET search_path TO "{schema}"'))

        existing_obj = await self.get_by_id(db, id=id)
        if not existing_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )

        try:
            existing_obj.is_deleted = True
            existing_obj.is_active = False
            existing_obj.deleted_at = datetime.datetime.utcnow()

            db.add(existing_obj)
            await db.commit()
        except Exception as ex:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(ex))

    # async def delete(self, db: AsyncSession, *, id: Any) -> None:
    #     """Delete a record by its ID."""
    #     existing_obj = await self.get_by_id(db, id=id)
    #     if not existing_obj:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=f"{self.model.__name__} not found"
    #         )

    #     try:
    #         await db.delete(existing_obj)
    #         await db.commit()
    #     except Exception as ex:
    #         await db.rollback()
    #         raise HTTPException(status_code=500, detail=str(ex))

    async def get_by_email(
            self, db: AsyncSession, *,
            email: Any,
    ) -> Optional[ModelType]:

        if id is None:
            return None
        existing_org = await db.execute(select(self.model).where(self.model.email == email))
        existing_org = existing_org.scalars().first()

        if not existing_org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )

        return existing_org

    def get_related_model(self, use_related_name: str):
        relation = getattr(self.model, use_related_name)
        if not isinstance(relation.prop, RelationshipProperty):
            raise AttributeError(f"{use_related_name} is not a valid relation")
        return relation, relation.prop.mapper.class_

    def _base(
            self,
            db: AsyncSession,
            fields=None,
            use_related_name: str = None,
            resource_id: int = None,
            joins: dict = None
    ):
        if use_related_name and resource_id:
            relation, related_model = self.get_related_model(use_related_name)
            if fields is not None:
                b_fields = [getattr(related_model, field.strip()) for field in fields]
            else:
                b_fields = [related_model]
            base = select(*b_fields).join(related_model, relation).where(self.model.id == resource_id)
            model = related_model
        else:
            if fields is not None:
                b_fields = [getattr(self.model, field.strip()) for field in fields]
            else:
                b_fields = [self.model]
            base = select(*b_fields)
            model = self.model

        if joins:
            target = self.model
            filters_dict = joins.get('filters', {})
            join_list = joins.get('joins', [])
            # Build a new base with the target model and apply filters
            base = select(target).where(*[getattr(target, key) == value for key, value in filters_dict.items()])
            for join in join_list:
                join_filters = join.get('filters', {})
                base = base.join(join['target']).where(
                    *[getattr(join['target'], key) == value for key, value in join_filters.items()]
                )
            model = target

        return model, base

    async def read(
            self,
            params: dict,
            db: AsyncSession,
            use_related_name: str = None,
            resource_id: int = None,
            joins: dict = {},
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ):
        """
        Read data using asynchronous SQLAlchemy session with flexible filters.
        Supports filtering, searching, and ordering.
        """
        try:

            # self.model.__table__.schema = "public"
            # await db.execute(text(f'SET search_path TO "public"'))

            # 1. Prepare the model and base statement
            model_to_filter, base = self._base(
                db,
                params.get('fields', None),
                use_related_name=use_related_name,
                resource_id=resource_id,
                joins=joins
            )

            # if hasattr(self.model, "organization"):
            #     from sqlalchemy.orm import selectinload
            #     base = base.options(selectinload(self.model.organization))

            # 2. Identify columns by type
            dt_cols = [col[0] for col in model_to_filter.c() if col[1] == datetime.datetime]
            ex_cols = [
                col[0] for col in model_to_filter.c()
                if col[1] == int or col[1] == bool or issubclass(col[1], enum.Enum)
            ]

            # 3. Separate filters by type
            dte_filters = {
                x: params[x] for x in params
                if x in dt_cols and params[x] is not None
            }
            ex_filters = {
                x: params[x] for x in params
                if x in ex_cols and params[x] is not None
            }
            ext_filters = {
                x: params[x] for x in params
                if x not in [
                    "offset", "limit", "q", "sort", "action", "fields",
                    *dt_cols, *ex_cols
                ] and params[x] is not None
            }

            # 4. Build filter list
            filters = []
            # String/enum columns
            filters.extend([
                getattr(model_to_filter, k) == v if v not in ['null', 0]
                else getattr(model_to_filter, k) == None
                for k, v in ext_filters.items()
            ])
            # Integer/bool/enum columns
            filters.extend([
                getattr(model_to_filter, k) == v if v not in ['null', 0]
                else getattr(model_to_filter, k) == None
                for k, v in ex_filters.items()
            ])
            # Datetime columns
            filters.extend([
                getattr(model_to_filter, k) >= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0] == 'gte'
                else getattr(model_to_filter, k) <= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[
                                                                                                 0] == 'lte'
                else getattr(model_to_filter, k) > str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0] == 'gt'
                else getattr(model_to_filter, k) < str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0] == 'lt'
                else getattr(model_to_filter, k) == str_to_datetime(val)
                for k, v in dte_filters.items() for val in v
            ])

            # 5. Apply filters
            base = base.filter(*filters)

            # 6. Sorting: use explicit order_by/order_direction if provided, otherwise fallback to params['sort']
            if order_by:
                order_field = getattr(model_to_filter, order_by, None)
                if not order_field:
                    raise ValueError(f"Invalid order_by column: {order_by}")
                base = base.order_by(order_field.asc() if order_direction == 'asc' else order_field.desc())
            elif params.get('sort'):
                sort_expressions = []
                for key in params['sort']:
                    if re.search(SORT_STR_X, key):
                        # Example: '-fieldname'
                        field_name = key[1:]  # remove leading '-'
                        sort_expressions.append(getattr(model_to_filter, field_name).desc())
                    else:
                        sort_expressions.append(getattr(model_to_filter, key).asc())
                base = base.order_by(*sort_expressions)

            # 7. Searching / "q" logic
            if params.get('q'):
                q_or_list = []
                fts_list = []
                for item in params['q']:
                    if re.search(Q_STR_X, item):
                        q_or_list.append(item)
                    else:
                        fts_list.append(item)

                # Example: simple equality or "null" check
                q_or_clause = or_(*[
                    getattr(model_to_filter, q.split(':')[0]) == q.split(':')[1]
                    if q.split(':')[1] not in ['null', 0]
                    else getattr(model_to_filter, q.split(':')[0]) == None
                    for q in q_or_list
                ])

                # Example: partial matching (ilike) on string columns
                fts_clause = or_(*[
                    getattr(model_to_filter, col[0]).ilike(f'%{val}%')
                    for col in model_to_filter.c()
                    if any((col[1] == str, issubclass(col[1], enum.Enum)))
                    for val in fts_list
                ])

                base = base.filter(fts_clause).filter(q_or_clause)

            # 8. Pagination: offset and limit
            data_stmt = base.offset(params['offset']).limit(params['limit'])
            data_result = await db.execute(data_stmt)
            data = data_result.scalars().all()
            count_stmt = base.with_only_columns(func.count('*')).order_by(None)
            count_result = await db.execute(count_stmt)
            bk_size = count_result.scalar() or 0

            return {
                'bk_size': bk_size,
                'pg_size': len(data),
                'data': data
            }
        except Exception as e:
            status_code, msg, class_name = 500, f'{e}', f"{e.__class__.__name__}"
            try:
                log.debug(__name__, e, 'critical')
            except Exception:
                pass

            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

    async def read_by_organization_id(
            self,
            organization_id: UUID4,
            params: dict,
            db: AsyncSession,
            use_related_name: str = None,
            resource_id: int = None,
            joins: dict = {},
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ):
        """
        Read data using an asynchronous SQLAlchemy session with flexible filters,
        after dynamically setting the tenant schema based on organization_id.
        """
        try:
            # 0. Retrieve the organization (in public schema) to determine the tenant schema.
            org_result = await db.execute(select(Organization).where(Organization.id == organization_id))
            organization_obj = org_result.scalars().first()
            if not organization_obj:
                raise HTTPException(status_code=404, detail="Organization not found")
            schema = organization_obj.domain_name

            # Set the schema on the model so subsequent queries target the tenant schema.
            self.model.__table__.schema = schema

            # Optionally, update the search_path so that unqualified tables use the tenant schema.
            await db.execute(text(f'SET search_path TO "{schema}"'))

            # 1. Prepare the model and base statement
            model_to_filter, base = self._base(
                db,
                params.get('fields', None),
                use_related_name=use_related_name,
                resource_id=resource_id,
                joins=joins
            )

            if hasattr(self.model, "organization"):
                from sqlalchemy.orm import selectinload
                base = base.options(selectinload(self.model.organization))

            # 2. Identify columns by type
            dt_cols = [col[0] for col in model_to_filter.c() if col[1] == datetime.datetime]
            ex_cols = [
                col[0] for col in model_to_filter.c()
                if col[1] == int or col[1] == bool or issubclass(col[1], enum.Enum)
            ]

            # 3. Separate filters by type
            dte_filters = {
                x: params[x] for x in params
                if x in dt_cols and params[x] is not None
            }
            ex_filters = {
                x: params[x] for x in params
                if x in ex_cols and params[x] is not None
            }
            ext_filters = {
                x: params[x] for x in params
                if x not in [
                    "offset", "limit", "q", "sort", "action", "fields",
                    *dt_cols, *ex_cols
                ] and params[x] is not None
            }

            # 4. Build filter list
            filters = []
            # String/enum columns
            filters.extend([
                getattr(model_to_filter, k) == v if v not in ['null', 0]
                else getattr(model_to_filter, k) == None
                for k, v in ext_filters.items()
            ])
            # Integer/bool/enum columns
            filters.extend([
                getattr(model_to_filter, k) == v if v not in ['null', 0]
                else getattr(model_to_filter, k) == None
                for k, v in ex_filters.items()
            ])
            # Datetime columns
            filters.extend([
                getattr(model_to_filter, k) >= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0] == 'gte'
                else getattr(model_to_filter, k) <= str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[
                                                                                                 0] == 'lte'
                else getattr(model_to_filter, k) > str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0] == 'gt'
                else getattr(model_to_filter, k) < str_to_datetime(val.split(":", 1)[1]) if val.split(":", 1)[0] == 'lt'
                else getattr(model_to_filter, k) == str_to_datetime(val)
                for k, v in dte_filters.items() for val in v
            ])

            # 5. Apply filters
            base = base.filter(*filters)

            # 6. Sorting: use explicit order_by/order_direction if provided, otherwise fallback to params['sort']
            if order_by:
                order_field = getattr(model_to_filter, order_by, None)
                if not order_field:
                    raise ValueError(f"Invalid order_by column: {order_by}")
                base = base.order_by(order_field.asc() if order_direction == 'asc' else order_field.desc())
            elif params.get('sort'):
                sort_expressions = []
                for key in params['sort']:
                    if re.search(SORT_STR_X, key):
                        # Example: '-fieldname'
                        field_name = key[1:]  # remove leading '-'
                        sort_expressions.append(getattr(model_to_filter, field_name).desc())
                    else:
                        sort_expressions.append(getattr(model_to_filter, key).asc())
                base = base.order_by(*sort_expressions)

            # 7. Searching / "q" logic
            if params.get('q'):
                q_or_list = []
                fts_list = []
                for item in params['q']:
                    if re.search(Q_STR_X, item):
                        q_or_list.append(item)
                    else:
                        fts_list.append(item)

                q_or_clause = or_(*[
                    getattr(model_to_filter, q.split(':')[0]) == q.split(':')[1]
                    if q.split(':')[1] not in ['null', 0]
                    else getattr(model_to_filter, q.split(':')[0]) == None
                    for q in q_or_list
                ])

                fts_clause = or_(*[
                    getattr(model_to_filter, col[0]).ilike(f'%{val}%')
                    for col in model_to_filter.c()
                    if any((col[1] == str, issubclass(col[1], enum.Enum)))
                    for val in fts_list
                ])

                base = base.filter(fts_clause).filter(q_or_clause)

            # 8. Pagination: offset and limit
            data_stmt = base.offset(params['offset']).limit(params['limit'])
            data_result = await db.execute(data_stmt)
            data = data_result.scalars().all()

            count_stmt = base.with_only_columns(func.count('*')).order_by(None)
            count_result = await db.execute(count_stmt)
            bk_size = count_result.scalar() or 0

            return {
                'bk_size': bk_size,
                'pg_size': len(data),
                'data': data
            }
        except Exception as e:
            status_code, msg, class_name = 500, f'{e}', f"{e.__class__.__name__}"
            try:
                log.debug(__name__, e, 'critical')
            except Exception:
                pass
            raise HTTPException(status_code=status_code, detail=raise_exc(msg=msg, type=class_name))

    async def create_schema(self, *, domain_name: str, db: AsyncSession):
        """Creates a new database schema dynamically."""
        await db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{domain_name}"'))
        await db.commit()

        Staff.__table__.schema = domain_name
        Department.__table__.schema = domain_name
        Appraisal.__table__.schema = domain_name
        AppraisalComment.__table__.schema = domain_name
        AppraisalInput.__table__.schema = domain_name
        AppraisalSubmission.__table__.schema = domain_name
        AppraisalTemplate.__table__.schema = domain_name
        DepartmentGroup.__table__.schema = domain_name
        FormFieldTemplate.__table__.schema = domain_name
        Role.__table__.schema = domain_name
        Permission.__table__.schema = domain_name
        OrganizationBranch.__table__.schema = domain_name
        OrganizationSettings.__table__.schema = domain_name
        appraisal_submission_comments.schema = domain_name
        role_permissions.schema = domain_name
        async with engine.begin() as conn:
            await conn.run_sync(APIBase.metadata.create_all)
