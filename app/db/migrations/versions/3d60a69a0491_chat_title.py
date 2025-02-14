"""chat_title

Revision ID: 3d60a69a0491
Revises: 7fb972aefde9
Create Date: 2024-10-31 15:04:56.444628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d60a69a0491'
down_revision = '7fb972aefde9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('title', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'title')
    # ### end Alembic commands ###
