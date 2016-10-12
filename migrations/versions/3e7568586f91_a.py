"""a

Revision ID: 3e7568586f91
Revises: None
Create Date: 2016-10-09 23:39:09.758917

"""

# revision identifiers, used by Alembic.
revision = '3e7568586f91'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    ### end Alembic commands ###
