import asyncio

from sqlalchemy import select

from src.core.database import async_session
from src.core.security import hash_password
from src.db.models.user import User, UserRole


async def create_admin():
    async with async_session() as session:

        username = input("Username: ")
        email = input("Email: ")
        password = input("Password: ")

        result = await session.execute(
            select(User).where(User.username == username)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("User already exists")
            return

        user = User(
            username=username,
            email=email,
            password=hash_password(password),
            role=UserRole.SUPERADMIN,
            is_active=True,
        )

        session.add(user)
        await session.commit()

        print("Super admin created successfully")


if __name__ == "__main__":
    asyncio.run(create_admin())