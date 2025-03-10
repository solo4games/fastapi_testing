"""Add DocumentsText Migartion

Revision ID: f2a0beed6517
Revises: c29214ea50e9
Create Date: 2024-12-19 13:21:17.930459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a0beed6517'
down_revision: Union[str, None] = 'c29214ea50e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('documents_text',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_doc', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['id_doc'], ['documents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('documents_text')
    # ### end Alembic commands ###
