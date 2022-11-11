"""ADD

Revision ID: 9076f7f1d1f1
Revises: 
Create Date: 2022-11-01 17:38:00.440829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9076f7f1d1f1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'business', 'countries', ['country_id'], ['id'])
    op.create_foreign_key(None, 'states', 'countries', ['countries_id'], ['id'])
    op.create_foreign_key(None, 'userdetail', 'countries', ['country_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'userdetail', type_='foreignkey')
    op.drop_constraint(None, 'states', type_='foreignkey')
    op.drop_constraint(None, 'business', type_='foreignkey')
    # ### end Alembic commands ###