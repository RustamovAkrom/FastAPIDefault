"""add audits table

Revision ID: b9a1c7d4a001
Revises: 385e09311891
Create Date: 2026-04-06 02:25:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b9a1c7d4a001"
down_revision: Union[str, None] = "385e09311891"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("query_params", sa.JSON(), nullable=True),
        sa.Column("request_body", sa.JSON(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("forwarded_for", sa.String(length=500), nullable=True),
        sa.Column("request_id", sa.String(length=36), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("is_suspicious", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audits_request_id"), "audits", ["request_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audits_request_id"), table_name="audits")
    op.drop_table("audits")
