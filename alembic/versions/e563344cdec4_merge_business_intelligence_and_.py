"""merge business intelligence and analytics migrations

Revision ID: e563344cdec4
Revises: 0fd8f4a0d773, 37e8630b7bab
Create Date: 2025-05-27 08:45:56.023095

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e563344cdec4'
down_revision = ('0fd8f4a0d773', '37e8630b7bab')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass