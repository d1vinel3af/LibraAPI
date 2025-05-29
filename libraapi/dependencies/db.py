from database.db import AsyncSessionLocal


async def async_get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()