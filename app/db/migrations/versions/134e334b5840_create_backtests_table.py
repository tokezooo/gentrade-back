"""create_backtests_table

Revision ID: 134e334b5840
Revises: 65610e92cb70
Create Date: 2025-01-10 11:55:43.561261

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "134e334b5840"
down_revision = "65610e92cb70"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "backtests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("strategy_id", sa.Integer(), nullable=False),
        sa.Column("file", sa.String(length=255), nullable=True),
        sa.Column("date_range", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["strategy_id"], ["strategies.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("backtests")
    # ### end Alembic commands ###
