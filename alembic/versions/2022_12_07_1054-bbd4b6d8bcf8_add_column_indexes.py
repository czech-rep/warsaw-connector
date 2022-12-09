"""add_column_indexes

Revision ID: bbd4b6d8bcf8
Revises: fde77a68e3dd
Create Date: 2022-12-07 10:54:17.735744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbd4b6d8bcf8'
down_revision = 'fde77a68e3dd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_bus_stops_stop_id'), 'bus_stops', ['stop_id'], unique=False)
    op.create_index(op.f('ix_tables_bus_stop'), 'tables', ['bus_stop'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tables_bus_stop'), table_name='tables')
    op.drop_index(op.f('ix_bus_stops_stop_id'), table_name='bus_stops')
    # ### end Alembic commands ###
