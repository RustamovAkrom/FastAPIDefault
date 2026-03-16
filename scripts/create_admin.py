import asyncio
import getpass

from sqlalchemy import select

from core.database import async_session
from core.security import hash_password
from core.settings import get_settings

from modules.users.models import User, UserRole


def prompt(value: str, default: str | None = None) -> str:
    """Prompt helper with default value."""
    if default:
        result = input(f"{value} [{default}]: ").strip()
        return result or default
    return input(f"{value}: ").strip()


async def create_admin() -> None:
    settings = get_settings()

    print("\n=== Create Super Admin ===\n")

    username = prompt("Username", settings.admin_user)
    email = prompt("Email")

    # normalize email
    email = email.strip().lower()

    if not email:
        print("❌ Email is required")
        return

    password = getpass.getpass("Password: ")

    if not password:
        password = settings.admin_password

    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("❌ Passwords do not match")
        return

    async with async_session() as session:

        # check username
        result = await session.execute(
            select(User).where(User.username == username)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("❌ Username already exists")
            return

        # check email
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing_email = result.scalar_one_or_none()

        if existing_email:
            print("❌ Email already exists")
            return

        user = User(
            username=username,
            email=email,
            password=hash_password(password),
            role=UserRole.SUPERADMIN,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            is_verified=True,
        )

        session.add(user)

        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print("❌ Failed to create admin:", e)
            return

        print("\n✅ Super admin created successfully\n")
        print(f"Username: {username}")
        print(f"Email: {email}")


if __name__ == "__main__":
    asyncio.run(create_admin())
