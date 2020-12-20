"""socials

Revision ID: b3d978c94df6
Revises: 230644aee241
Create Date: 2020-09-12 16:30:13.667242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3d978c94df6'
down_revision = '230644aee241'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('social_links',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reddit', sa.String(length=120), nullable=True),
    sa.Column('steam', sa.String(length=120), nullable=True),
    sa.Column('twitch', sa.String(length=120), nullable=True),
    sa.Column('twitter', sa.String(length=120), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('social_links')
    # ### end Alembic commands ###