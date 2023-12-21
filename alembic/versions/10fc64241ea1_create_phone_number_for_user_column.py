"""Create phone number for user column

Revision ID: 10fc64241ea1
Revises: 
Create Date: 2023-12-14 12:34:52.287141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10fc64241ea1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('phone_number',sa.String(),nullable=True))


def downgrade() -> None:
    op.drop_column('users','phone_number')
