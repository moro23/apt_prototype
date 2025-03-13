from fastapi import Request, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from config.logger import log
from config.settings import settings

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


async def get_schema(request: Request) -> str:
    return getattr(request.state, "schema", "public")


async def get_db(schema: str = Depends(get_schema)) -> AsyncSession:
    async with AsyncSessionLocal() as db:
        try:
            # Set search path outside the main transaction
            # Use a separate connection execution
            connection = await db.connection()
            await connection.execute(text(f'SET search_path TO "{schema}"'))

            # Now yield the session for use
            yield db

            # If we got here, commit any pending transaction
            await db.commit()
        except Exception:
            # If an exception occurred, roll back
            await db.rollback()
            raise
        finally:
            # Try to reset search path, but in a new connection if needed
            try:
                # This might fail if the transaction is aborted
                connection = await db.connection()
                await connection.execute(text('SET search_path TO "public"'))
            except:
                log.exception("Failed to set search path")
                pass


async def drop_and_alter_table_columns(db: AsyncSession):
    # Await the query execution
    result = await db.execute(text('SELECT username FROM public.users'))
    org_names = result.scalars().all()

    if org_names:
        # Await the execution of the DDL command
        await db.execute(text('ALTER TABLE public.organizations ADD COLUMN acces_url VARCHAR DEFAULT NULL'))
        await db.commit()
        print("Column added successfully")
    else:
        print("Table not found")
