"""initial migration

Revision ID: f2712699b31d
Revises: 
Create Date: 2024-04-29 14:15:38.365133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2712699b31d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('account',
    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
    sa.Column('uid', sa.Integer(), index=True, unique=True),
    sa.Column('login', sa.String(64), index=True, unique=True),
    sa.Column('deleted', sa.Boolean(), default=False, nullable=False),
    sa.Column('to_keep', sa.Boolean(), default=False, nullable=False),
    sa.Column('locked', sa.Boolean(), default=False, nullable=False)
    )

    op.create_table('account_storage_time',
    sa.Column('account_id', sa.Integer(), sa.ForeignKey('account.id'), primary_key=True),
    sa.Column('since', sa.DateTime(), primary_key=True),
    sa.Column('until', sa.DateTime()),
    sa.Column('reason', sa.String(128))
    )

    op.create_table('action',
    sa.Column('action_id', sa.Integer(), primary_key=True, autoincrement=True),
    sa.Column('label', sa.String(64), index=True, unique=True),
    sa.Column('description', sa.String(128))
    )

    op.create_table('history',
    sa.Column('history_id', sa.Integer(), primary_key=True, autoincrement=True),
    sa.Column('date_action', sa.DateTime()),
    sa.Column('account_id', sa.Integer(), sa.ForeignKey('account.id')),
    sa.Column('action_id', sa.Integer(), sa.ForeignKey('action.action_id')),
    sa.Column('reason', sa.String(128))
    )


def downgrade():
    op.drop_table('template_mail')
    op.drop_table('action')
    op.drop_table('account_storage_time')
    op.drop_table('account')
