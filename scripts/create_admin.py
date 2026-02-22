import asyncio

from src.core.database import async_session
from src.db.models.user import User, UserRole
from src.core.security import hash_password


async def create_admin():
    async with async_session() as session:
        admin = User(
            username="admin",
            email="admin@mail.com",
            password=hash_password("admin123"),
            role=UserRole.SUPERADMIN.value
        )

        session.add(admin)
        await session.commit()

        print("Admin created successfully")


if __name__ == "__main__":
    asyncio.run(create_admin())
