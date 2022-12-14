"""initial_empty

Revision ID: fde77a68e3dd
Revises: 
Create Date: 2022-12-05 17:14:59.972979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fde77a68e3dd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bus_stops',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stop_id', sa.String(length=10), nullable=False),
    sa.Column('number', sa.String(length=10), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stop_id', 'number', name='unique_stop_id_number')
    )
    op.create_table('lines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('line_number', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('line_number')
    )
    op.create_table('bus_stop_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bus_stop_id', sa.Integer(), nullable=False),
    sa.Column('street_id', sa.String(length=20), nullable=True),
    sa.Column('geo_width', sa.String(length=20), nullable=False),
    sa.Column('geo_length', sa.String(length=20), nullable=False),
    sa.Column('direction', sa.String(length=60), nullable=True),
    sa.Column('valid_from', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['bus_stop_id'], ['bus_stops.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('bus_stop_id', 'valid_from', name='unique_stop_id_date')
    )
    op.create_table('bus_stop_lines',
    sa.Column('bus_stop_id', sa.Integer(), nullable=False),
    sa.Column('line_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bus_stop_id'], ['bus_stops.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['line_id'], ['lines.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('bus_stop_id', 'line_id')
    )
    op.create_table('tables',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('brigade', sa.String(length=10), nullable=False),
    sa.Column('direction', sa.String(length=50), nullable=False),
    sa.Column('route', sa.String(length=20), nullable=False),
    sa.Column('time', sa.Time(), nullable=False),
    sa.Column('bus_stop', sa.Integer(), nullable=False),
    sa.Column('line', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bus_stop'], ['bus_stops.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['line'], ['lines.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('brigade', 'bus_stop', 'line', 'time', name='one_brigade_of_line_on_stop_at_time')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tables')
    op.drop_table('bus_stop_lines')
    op.drop_table('bus_stop_data')
    op.drop_table('lines')
    op.drop_table('bus_stops')
    # ### end Alembic commands ###
