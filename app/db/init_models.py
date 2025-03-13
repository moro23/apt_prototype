import asyncio

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from config.settings import settings
from db.session import engine

SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL


async def create_database():
    if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
        db_name = SQLALCHEMY_DATABASE_URL.split("/")[-1]
        temp_engine = create_async_engine(SQLALCHEMY_DATABASE_URL.rsplit("/", 1)[0] + "/postgres")

        async with temp_engine.connect() as conn:
            try:
                await conn.execution_options(isolation_level="AUTOCOMMIT")

                result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
                if result.scalar():
                    return

                await conn.execute(text(f"CREATE DATABASE {db_name}"))
            except ProgrammingError:
                pass


async def init_database():
    print("Starting database")
    await create_database()


from domains.organization.models.organization import Organization
from domains.organization.models.bill import Bill
from domains.organization.models.payment import Payment
from domains.organization.models.tenancy import Tenancy
from domains.organization.models.terms_and_conditions import TermsAndConditions
from domains.auth.models.refresh_token import RefreshToken
from domains.appraisal.models.appraisal_template import AppraisalTemplate
from domains.auth.models.users import User
from domains.auth.models.role_permissions import Role


async def create_selected_tables(engine: AsyncEngine):
    """Creates only the selected models in the database."""
    selected_models = [
        Organization, TermsAndConditions, Tenancy, Bill,
        Payment, User, RefreshToken, AppraisalTemplate, Role
    ]

    async with engine.begin() as conn:
        for model in selected_models:
            model.__table__.schema = "public"
            await conn.run_sync(model.__table__.create, checkfirst=True)


async def init_tables():
    """Initialize only selected tables."""
    await create_selected_tables(engine)


if __name__ == "__main__":
    asyncio.run(init_tables())
