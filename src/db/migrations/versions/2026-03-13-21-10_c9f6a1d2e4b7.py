"""merge heads after permissions v1

Revision ID: c9f6a1d2e4b7
Revises: 754b05e8ad8f, 7a1d3f9c9b10
Create Date: 2026-03-13 21:10:00.000000

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "c9f6a1d2e4b7"
down_revision: Union[str, Sequence[str], None] = ("754b05e8ad8f", "7a1d3f9c9b10")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration with no schema changes."""


def downgrade() -> None:
    """Downgrade merge migration with no schema changes."""
