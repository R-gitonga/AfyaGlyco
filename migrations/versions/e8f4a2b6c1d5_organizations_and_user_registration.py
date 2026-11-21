"""Add organizations and organization-scoped registration metadata.

Revision ID: e8f4a2b6c1d5
Revises: d7e3f9a1b2c4
"""

from alembic import op
import sqlalchemy as sa


revision = "e8f4a2b6c1d5"
down_revision = "d7e3f9a1b2c4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("organization_type", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"])

    op.add_column("users", sa.Column("display_name", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_index("ix_users_organization_id", "users", ["organization_id"])
    op.create_foreign_key(
        "fk_users_organization_id",
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "patient_profiles",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_patient_profiles_organization_id",
        "patient_profiles",
        ["organization_id"],
    )
    op.create_foreign_key(
        "fk_patient_profiles_organization_id",
        "patient_profiles",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO organizations
                (name, organization_type, is_active, created_at, updated_at)
            VALUES
                ('AfyaGlyco Demo Clinic', 'clinic', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
        )
    )
    bind.execute(
        sa.text(
            """
            UPDATE users
            SET organization_id = (
                SELECT id FROM organizations WHERE name = 'AfyaGlyco Demo Clinic'
            )
            WHERE id IN (
                SELECT role_assignments.user_id
                FROM role_assignments
                JOIN roles ON roles.id = role_assignments.role_id
                WHERE roles.name IN ('clinician', 'patient')
            )
            """
        )
    )
    bind.execute(
        sa.text(
            """
            UPDATE patient_profiles
            SET organization_id = users.organization_id
            FROM users
            WHERE users.id = patient_profiles.user_id
            """
        )
    )


def downgrade():
    op.drop_constraint(
        "fk_patient_profiles_organization_id", "patient_profiles", type_="foreignkey"
    )
    op.drop_index(
        "ix_patient_profiles_organization_id", table_name="patient_profiles"
    )
    op.drop_column("patient_profiles", "organization_id")
    op.drop_constraint("fk_users_organization_id", "users", type_="foreignkey")
    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_column("users", "organization_id")
    op.drop_column("users", "display_name")
    op.drop_index("ix_organizations_name", table_name="organizations")
    op.drop_table("organizations")
