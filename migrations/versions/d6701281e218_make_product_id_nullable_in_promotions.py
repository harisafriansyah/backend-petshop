"""Make product_id nullable in promotions

Revision ID: d6701281e218
Revises: ef00b5e1707a
Create Date: 2024-12-18 21:18:46.463867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6701281e218'
down_revision = 'ef00b5e1707a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.alter_column('product_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.alter_column('product_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
