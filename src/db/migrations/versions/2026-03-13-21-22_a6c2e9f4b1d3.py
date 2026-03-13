"""merge heads after update permission draft

Revision ID: a6c2e9f4b1d3
Revises: d5b1b392c205, f2c4b8a1d0e5
Create Date: 2026-03-13 21:22:00.000000

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "a6c2e9f4b1d3"
down_revision: Union[str, Sequence[str], None] = ("d5b1b392c205", "f2c4b8a1d0e5")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration with no schema changes."""


def downgrade() -> None:
    """Downgrade merge migration with no schema changes."""
