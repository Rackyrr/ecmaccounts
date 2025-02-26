"""remove column to_keep from account, column not necessary

Revision ID: 2500e2917b06
Revises: 780060577217
Create Date: 2024-05-06 15:49:57.958126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2500e2917b06'
down_revision = '780060577217'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('to_keep')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('to_keep', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
