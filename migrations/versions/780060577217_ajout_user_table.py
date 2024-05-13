"""ajout user table

Revision ID: 780060577217
Revises: 3852558b8b29
Create Date: 2024-05-02 14:26:56.022051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '780060577217'
down_revision = '3852558b8b29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('login', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_login'), ['login'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_token'), ['token'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_token'))
        batch_op.drop_index(batch_op.f('ix_user_login'))

    op.drop_table('user')
    # ### end Alembic commands ###
