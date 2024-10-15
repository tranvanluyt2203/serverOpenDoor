"""empty message

Revision ID: f08e25b7bb18
Revises: ad088a44f37c
Create Date: 2024-10-15 20:25:57.840718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f08e25b7bb18'
down_revision = 'ad088a44f37c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weather',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('temp', sa.Float(), nullable=False),
    sa.Column('humidity', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('weather')
    # ### end Alembic commands ###