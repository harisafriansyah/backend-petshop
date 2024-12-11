"""Add domain and address to stores

Revision ID: a901e0395c61
Revises: 3948ad8f51fa
Create Date: 2024-12-10 22:56:46.756043

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a901e0395c61'
down_revision = '3948ad8f51fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nama_domain', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('alamat_lengkap', sa.Text(), nullable=False))
        batch_op.add_column(sa.Column('deskripsi_toko', sa.Text(), nullable=True))
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=20),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('updated_at',
               existing_type=mysql.DATETIME(),
               nullable=True)
        batch_op.create_unique_constraint(None, ['nama_domain'])
        batch_op.drop_column('shop_description')
        batch_op.drop_column('no_tlp')
        batch_op.drop_column('alamat_toko')
        batch_op.drop_column('no_rek')
        batch_op.drop_column('bank')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bank', mysql.VARCHAR(collation='utf8mb4_general_ci', length=200), nullable=False))
        batch_op.add_column(sa.Column('no_rek', mysql.VARCHAR(collation='utf8mb4_general_ci', length=50), nullable=False))
        batch_op.add_column(sa.Column('alamat_toko', mysql.VARCHAR(collation='utf8mb4_general_ci', length=200), nullable=False))
        batch_op.add_column(sa.Column('no_tlp', mysql.VARCHAR(collation='utf8mb4_general_ci', length=15), nullable=False))
        batch_op.add_column(sa.Column('shop_description', mysql.TEXT(collation='utf8mb4_general_ci'), nullable=True))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('updated_at',
               existing_type=mysql.DATETIME(),
               nullable=False)
        batch_op.alter_column('status',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(collation='utf8mb4_general_ci', length=20),
               existing_nullable=True)
        batch_op.drop_column('deskripsi_toko')
        batch_op.drop_column('alamat_lengkap')
        batch_op.drop_column('nama_domain')

    # ### end Alembic commands ###
