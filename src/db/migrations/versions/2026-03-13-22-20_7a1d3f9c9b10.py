"""add permissions v1

Revision ID: 7a1d3f9c9b10
Revises: be58262522f0
Create Date: 2026-03-13 22:20:00.000000

"""

from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7a1d3f9c9b10"
down_revision: Union[str, None] = "be58262522f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "permissions",
        sa.Column("codename", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("module", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permissions_codename"), "permissions", ["codename"], unique=True)

    op.create_table(
        "role_permissions",
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role", "permission_id", name="uq_role_permission_role_perm"),
    )
    op.create_index(op.f("ix_role_permissions_role"), "role_permissions", ["role"], unique=False)

    op.create_table(
        "user_permissions",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("is_granted", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "permission_id", name="uq_user_permission_user_perm"),
    )
    op.create_index(op.f("ix_user_permissions_user_id"), "user_permissions", ["user_id"], unique=False)

    now = datetime.utcnow()
    permissions_table = sa.table(
        "permissions",
        sa.column("codename", sa.String),
        sa.column("name", sa.String),
        sa.column("module", sa.String),
        sa.column("description", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    op.bulk_insert(
        permissions_table,
        [
            {
                "codename": "users.view_user",
                "name": "Can view users",
                "module": "users",
                "description": "View user list and details",
                "created_at": now,
                "updated_at": now,
            },
            {
                "codename": "users.add_user",
                "name": "Can add users",
                "module": "users",
                "description": "Create users",
                "created_at": now,
                "updated_at": now,
            },
            {
                "codename": "users.change_user",
                "name": "Can change users",
                "module": "users",
                "description": "Edit users and perform change actions",
                "created_at": now,
                "updated_at": now,
            },
            {
                "codename": "users.delete_user",
                "name": "Can delete users",
                "module": "users",
                "description": "Delete users",
                "created_at": now,
                "updated_at": now,
            },
        ],
    )

    op.execute(
        """
        INSERT INTO role_permissions (role, permission_id, created_at, updated_at)
        SELECT 'admin', p.id, now(), now()
        FROM permissions p
        WHERE p.codename IN ('users.view_user', 'users.add_user', 'users.change_user', 'users.delete_user')
        """
    )
    op.execute(
        """
        INSERT INTO role_permissions (role, permission_id, created_at, updated_at)
        SELECT 'moderator', p.id, now(), now()
        FROM permissions p
        WHERE p.codename IN ('users.view_user', 'users.change_user')
        """
    )
    op.execute(
        """
        INSERT INTO role_permissions (role, permission_id, created_at, updated_at)
        SELECT 'user', p.id, now(), now()
        FROM permissions p
        WHERE p.codename IN ('users.view_user')
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_user_permissions_user_id"), table_name="user_permissions")
    op.drop_table("user_permissions")

    op.drop_index(op.f("ix_role_permissions_role"), table_name="role_permissions")
    op.drop_table("role_permissions")

    op.drop_index(op.f("ix_permissions_codename"), table_name="permissions")
    op.drop_table("permissions")
