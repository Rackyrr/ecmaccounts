"""ajout table template mail

Revision ID: 3852558b8b29
Revises: 3082e097c908
Create Date: 2024-05-02 14:22:15.681838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3852558b8b29'
down_revision = '3082e097c908'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('template_mail',
    sa.Column('title_template', sa.String(length=64), nullable=False),
    sa.Column('subject', sa.String(length=64), nullable=True),
    sa.Column('body', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('title_template')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('template_mail')
    # ### end Alembic commands ###
