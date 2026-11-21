"""Repair the user display-name column after the Sprint 9 migration.

Some development databases were stamped at the Sprint 9 revision after the
migration file had been applied without the later ``display_name`` addition.
This corrective migration is conditional so it is safe for both those
databases and fresh databases where the column already exists.
"""

from alembic import op
import sqlalchemy as sa


revision = "f3a7c9d1e2b4"
down_revision = "e8f4a2b6c1d5"
branch_labels = None
depends_on = None


def upgrade():
    # Only add the column when an older database was stamped before it existed.
    inspector = sa.inspect(op.get_bind())
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "display_name" not in user_columns:
        op.add_column("users", sa.Column("display_name", sa.String(length=120), nullable=True))


def downgrade():
    # Keep downgrade safe for databases where the repair found nothing to add.
    inspector = sa.inspect(op.get_bind())
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "display_name" in user_columns:
        op.drop_column("users", "display_name")
