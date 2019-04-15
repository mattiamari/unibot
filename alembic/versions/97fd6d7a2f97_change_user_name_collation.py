"""change user name collation

Revision ID: 97fd6d7a2f97
Revises:
Create Date: 2019-04-15 11:00:01.478287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97fd6d7a2f97'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("alter database unibot collate='utf8mb4_unicode_ci'")
    op.execute("alter table unibot.user convert to character set utf8mb4 collate 'utf8mb4_unicode_ci'")
    op.execute("alter table unibot.user_settings convert to character set utf8mb4 collate 'utf8mb4_unicode_ci'")


def downgrade():
    pass
