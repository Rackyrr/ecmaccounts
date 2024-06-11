"""add last connection details

Revision ID: 6a87b5f158d7
Revises: 681221371ec2
Create Date: 2024-06-10 15:09:13.360353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a87b5f158d7'
down_revision = '681221371ec2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_connection_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('last_connection_ip', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('last_connection_type', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('last_connection_service', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('last_connection_service')
        batch_op.drop_column('last_connection_type')
        batch_op.drop_column('last_connection_ip')
        batch_op.drop_column('last_connection_date')

    # ### end Alembic commands ###
