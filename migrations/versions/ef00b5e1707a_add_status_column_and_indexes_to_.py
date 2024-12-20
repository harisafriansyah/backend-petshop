"""Add status column and indexes to promotions

Revision ID: ef00b5e1707a
Revises: 
Create Date: 2024-12-18 21:07:57.089163

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef00b5e1707a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=True))
        batch_op.create_index('idx_promotion_period', ['promotion_period_start', 'promotion_period_end'], unique=False)
        batch_op.create_unique_constraint('uq_product_promotion', ['product_id', 'promotion_period_start'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.drop_constraint('uq_product_promotion', type_='unique')
        batch_op.drop_index('idx_promotion_period')
        batch_op.drop_column('status')

    # ### end Alembic commands ###
