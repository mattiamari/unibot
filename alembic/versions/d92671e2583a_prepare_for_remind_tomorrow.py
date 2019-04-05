"""prepare for remind_tomorrow

Revision ID: d92671e2583a
Revises:
Create Date: 2019-04-05 13:58:19.081181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd92671e2583a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user_settings', 'do_remind', new_column_name='do_remind_today')
    op.alter_column('user_settings', 'remind_time', new_column_name='remind_time_today')
    op.add_column('user_settings', sa.Column('do_remind_tomorrow', sa.Boolean, default=False))
    op.add_column('user_settings', sa.Column('remind_time_tomorrow', sa.Time, default=None))


def downgrade():
    pass
