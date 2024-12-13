"""Fix backref conflict in User and Store models

Revision ID: ecd02bbf7de6
Revises: fe2dadc5df2a
Create Date: 2024-12-07 10:16:08.686224

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ecd02bbf7de6'
down_revision = 'fe2dadc5df2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('no_tlp', sa.String(length=15), nullable=False))
        batch_op.alter_column('no_rek',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=20),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.drop_constraint('stores_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])
        batch_op.drop_column('penjual_id')
        batch_op.drop_column('no_telp')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('no_telp', mysql.VARCHAR(collation='utf8mb4_general_ci', length=15), nullable=False))
        batch_op.add_column(sa.Column('penjual_id', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('stores_ibfk_1', 'users', ['penjual_id'], ['id'], ondelete='CASCADE')
        batch_op.alter_column('no_rek',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(collation='utf8mb4_general_ci', length=20),
               existing_nullable=False)
        batch_op.drop_column('no_tlp')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###