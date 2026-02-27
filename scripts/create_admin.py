import asyncio

from sqlalchemy import select

from core.database import async_session
from core.security import hash_password
from db.models.user import User, UserRole
from core.settings import get_settings

async def create_admin():
    settings = get_settings()

    async with async_session() as session:

        username = input(f"Username [{settings.admin_user}]: ")
        email = input("Email: ")
        password = input(f"Password: [{settings.admin_password}]:")

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