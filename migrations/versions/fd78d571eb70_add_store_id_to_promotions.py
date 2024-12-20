"""Add store_id to promotions

Revision ID: fd78d571eb70
Revises: cd5205fd5569
Create Date: 2024-12-20 05:41:03.824078

"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = 'fd78d571eb70'
down_revision = 'cd5205fd5569'
branch_labels = None
depends_on = None

def upgrade():
    # Tambahkan kolom store_id dengan nullable=True terlebih dahulu
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('store_id', sa.Integer(), nullable=True))

    # Update semua baris yang ada dengan nilai default untuk store_id
    op.execute('UPDATE promotions SET store_id = 1')  # Ganti 1 dengan store_id default Anda

    # Ubah kolom store_id menjadi NOT NULL
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.alter_column('store_id', nullable=False)

def downgrade():
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.drop_column('store_id')

