from datetime import datetime
from typing import (
    Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Literal, Sequence, Tuple
)

from fastapi import HTTPException
from pydantic import BaseModel, UUID4
from sqlalchemy import or_, desc, select, delete, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from config.logger import log
from db.base_class import APIBase
from db.session import engine
from utils.exceptions import http_500_exc_internal_server_error

ModelType = TypeVar("ModelType", bound=APIBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations on database models.

    Provides common database operations with error handling and type safety.

    Type Parameters:
        ModelType: The SQLAlchemy model type
        CreateSchemaType: Pydantic model for creation operations
        UpdateSchemaType: Pydantic model for update operations
    """

    def __init__(self, model: Type[ModelType], select_related: Tuple = None):
        """
        Initialize the repository with a specific model.

        Args:
            model: SQLAlchemy model class
            select_related: Tuple of SQLAlchemy model related columns
        """
        self.model = model
        self.query = select(self.model)
        if select_related is not None:
            fields_to_select = (selectinload(field) for field in select_related)
            self.query = select(self.model).options(*fields_to_select)

    async def get_by_id(
            self, db: AsyncSession, *,
            id: Any,
            silent: bool = False,
    ) -> Optional[ModelType]:
        """
        Retrieve a single record by its ID.

        Args:
            db: Database session
            id: Primary key value
            silent: If True, return None instead of raising 404 when not found

        Returns:
            Optional[ModelType]: Found record or None if silent=True

        Raises:
            HTTPException: 404 if record not found and silent=False
        """
        if id is None: return None
        try:
            result = await db.execute(
                self.query.filter(self.model.id == id)
            )
            return result.scalar_one()
        except NoResultFound:
            if silent: return None
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )
        except SQLAlchemyError:
            log.error(f"Database error fetching {self.model.__name__} with id={id}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )
        except:
            log.exception(f"Unexpected error fetching {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_by_field(self, db: AsyncSession, *, field: str, value: Any) -> Optional[ModelType]:
        """
        Retrieve a single record by matching a specific field value.

        Args:
            db: Database session
            field: Model field name
            value: Value to match

        Returns:
            Optional[ModelType]: Found record or None

        Raises:
            HTTPException: 400 if field is invalid
        """
        if value is None: return None

        try:
            result = await db.execute(
                self.query.filter(getattr(self.model, field) == value)
            )
            return result.scalar_one_or_none()
        except AttributeError:
            log.error(f"Invalid field {field} for model {self.model.__name__}", exc_info=True)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=f'Invalid field: {field}'
            )
        except:
            log.exception(f"Error in get_by_field for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_many_by_ids(self, db: AsyncSession, *, ids: List[Any]) -> Sequence[ModelType]:
        """
        Retrieve multiple records by their IDs.

        Args:
            db: Database session
            ids: List of primary key values

        Returns:
            List[ModelType]: List of found records

        Raises:
            HTTPException: 400 if any ID is not found
        """
        if not ids: return []
        try:
            result = await db.execute(
                self.query.filter(self.model.id.in_(ids))
            )
            found_objects = result.scalars().all()

            missing_ids = set(ids) - {obj.id for obj in found_objects}
            if missing_ids: raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Records not found for ids: {missing_ids}"
            )
            return found_objects
        except HTTPException:
            raise
        except:
            log.exception(f"Error in get_many_by_ids for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_all(
            self, *,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> Sequence[ModelType]:
        """
        Retrieve all records with pagination and ordering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_direction: Sort direction ('asc' or 'desc')

        Returns:
            List[ModelType]: List of records
        """
        try:
            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = self.query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )
            else:
                query = self.query.order_by(desc(self.model.created_date))

            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {self.model.__name__}", exc_info=True)
            return []
        except:
            log.exception(f"Unexpected error in get_all {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_by_filters(
            self, *,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **filters: Any
    ) -> Sequence[ModelType]:
        """
        Retrieve records matching exact filter conditions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_direction: Sort direction ('asc' or 'desc')
            **filters: Field-value pairs to filter by

        Returns:
            List[ModelType]: List of matching records
        """
        query = self.query
        try:
            # Apply filters
            for field, value in filters.items():
                if value is not None: query = query.filter(getattr(self.model, field) == value)

            # Apply ordering
            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )

            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()

        except HTTPException:
            raise
        except AttributeError as e:
            log.error(f"Invalid filter field")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f'Invalid filter field provided for {self.model.__name__}'
            )
        except:
            log.exception(f"Error in get_by_filters for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_by_pattern(
            self, *,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **patterns: Any
    ) -> Sequence[ModelType]:
        """
        Retrieve records matching pattern-based (ILIKE) filter conditions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_direction: Sort direction ('asc' or 'desc')
            **patterns: Field-pattern pairs to filter by

        Returns:
            List[ModelType]: List of matching records
        """
        query = self.query
        try:
            # Apply pattern matching filters
            for field, pattern in patterns.items():
                if not pattern: continue

                field_attr = getattr(self.model, field)
                if isinstance(pattern, list):
                    valid_patterns = [p for p in pattern if p]
                    if valid_patterns:
                        query = query.filter(or_(*[field_attr.ilike(f"%{p}%") for p in valid_patterns]))
                    else:  # todo test without else clause
                        continue
                else:
                    query = query.filter(field_attr.ilike(f"%{pattern}%"))

            # Apply ordering
            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )

            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()

        except HTTPException:
            raise
        except AttributeError as e:
            log.error(f"Invalid pattern matching field", exc_info=True)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=f'Invalid field for pattern matching: {str(e)}'
            )
        except:
            log.exception(f"Error in get_by_pattern for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_or_create(
            self, *,
            db: AsyncSession,
            data: CreateSchemaType,
            unique_field: str,
    ) -> ModelType:
        """
        Find an existing record by a unique field or create a new one.

        Args:
            db: Database session
            data: Creation data
            unique_field: Field to check for existing record

        Returns:
            ModelType: Existing or newly created record
        """
        try:
            # Try to find existing record
            result = await db.execute(
                self.query.filter(getattr(self.model, unique_field) == getattr(data, unique_field))
            )
            existing = result.scalar_one_or_none()
            if existing: return existing

            # Create new record if not found
            return await self.create(db=db, data=data)
        except:
            log.exception(f"Error in get_or_create for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def create(self, db: AsyncSession, *, data: CreateSchemaType, unique_fields: list = None) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            data: Creation data

        Returns:
            ModelType: Created record

        Raises:
            HTTPException: 409 on unique constraint violation
        """
        if unique_fields is None: unique_fields = []
        if not data: raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="No data provided for creation"
        )

        try:
            model_data = data.model_dump(exclude_none=True, exclude_defaults=False)
            await self.validate_unique_fields(db=db, model_data=model_data, unique_fields=unique_fields)

            db_obj = self.model(**model_data)
            db.add(db_obj)
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            log.error(f"Integrity error creating {self.model.__name__}", exc_info=True)
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=self._format_integrity_error(e))
        except:
            await db.rollback()
            log.exception(f"Error creating {self.model.__name__}")
            raise await http_500_exc_internal_server_error()
        else:
            return await self.get_by_id(db=db, id=db_obj.id)

    async def update(
            self, *,
            db: AsyncSession,
            data: Union[UpdateSchemaType, Dict[str, Any]],
            db_obj: Optional[ModelType] = None,
            id: Optional[UUID4] = None,
            unique_fields: Optional[List] = None
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db: Database session
            data: Update data (Pydantic model or dict)
            db_obj: Existing record to update
            id: Id of the record to update
            unique_fields: Fields to check if they already exist

        Returns:
            ModelType: Updated record
        """
        if unique_fields is None: unique_fields = []

        if not db_obj and not id: raise NotImplementedError(
            "Either the db_obj or id must be given!!!"
        )
        if not db_obj: db_obj = await self.get_by_id(db=db, id=id)

        try:
            update_data = data.model_dump(exclude_none=True) if isinstance(data, BaseModel) else data
            await self.validate_unique_fields(db=db, model_data=update_data, unique_fields=unique_fields)

            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except:
            await db.rollback()
            log.exception(f"Error updating {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def delete(self, db: AsyncSession, *, id: UUID4, soft: bool =False) -> None:
        """
        Delete a record by ID.

        Args:
            db: Database session
            id: Record ID to delete
            soft: argument to either soft delete the record or not

        Raises:
            HTTPException: 404 if not found, 409 if deletion violates constraints
        """
        # Check existence
        existing_obj = await self.get_by_id(db=db, id=id)
        try:
            if soft:
                existing_obj.is_deleted = True
                existing_obj.is_active = False
                existing_obj.deleted_at = datetime.utcnow()

                # Mark the object as changed
                db.add(existing_obj)
                await db.commit()
            else:
                # Perform hard deletion
                await db.execute(
                    delete(self.model)
                    .where(self.model.id == id)
                    .execution_options(synchronize_session=False)
                )
                await db.commit()
        except IntegrityError:
            await db.rollback()
            log.error(f"Integrity error deleting {self.model.__name__}", exc_info=True)
        except:
            log.exception(f"Error deleting {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def reactivate(self, db: AsyncSession, *, id: UUID4) -> None:
        """Soft-delete a record by its ID by setting is_deleted to True, is_active to False, and deleted_at to current time."""
        existing_obj = await self.get_by_id(db, id=id)
        if not existing_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        try:
            existing_obj.is_deleted = False
            existing_obj.is_active = True
            existing_obj.deleted_at = None

            # Mark the object as changed
            db.add(existing_obj)
            await db.commit()
        except:
            await db.rollback()
            log.exception("Failed to reactivate {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    @staticmethod
    def _format_integrity_error(e: IntegrityError) -> str:
        """Prettifies SQLAlchemy IntegrityError messages."""
        error_message = str(e.orig)

        if isinstance(e.orig, Exception):
            if "ForeignKeyViolationError" in error_message:
                start = error_message.find("Key (")
                if start != -1:
                    detail = error_message[start:].replace("DETAIL: ", "").strip()
                    return f"Foreign key constraint violated: {detail}"
                return "Foreign key constraint violated."
            elif "UniqueViolationError" in error_message:
                return "Unique constraint violated. A similar record already exists."

        return str(e.orig)

    async def validate_unique_fields(self, db: AsyncSession, *, model_data: dict, unique_fields: List):
        for field in unique_fields:
            if field in model_data and model_data[field]:
                query = select(self.model).where(getattr(self.model, field) == model_data[field])
                result = await db.execute(query)
                if result.scalars().first(): raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{field}' for {model_data[field]} already exists"
                )

    async def create_schema(self, *, domain_name: str, db: AsyncSession):
        """Creates a new database schema dynamically."""

        from domains.appraisal.models.appraisal import Appraisal
        from domains.appraisal.models.appraisal_comment import AppraisalComment, appraisal_submission_comments
        from domains.appraisal.models.appraisal_input import AppraisalInput
        from domains.appraisal.models.appraisal_submission import AppraisalSubmission
        from domains.appraisal.models.appraisal_template import AppraisalTemplate
        from domains.appraisal.models.department_group import DepartmentGroup
        from domains.auth.models.role_permissions import Role, role_permissions, Permission
        from domains.organization.models.form_template import FormFieldTemplate
        from domains.organization.models.organization_branch import OrganizationBranch
        from domains.organization.models.organization_settings import OrganizationSettings
        from domains.staff.models.department import Department
        from domains.staff.models.staff import Staff

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
