"""Add medication reminders and patient-entered events.

Revision ID: d7e3f9a1b2c4
Revises: c4f6a1e2b7d3
"""

from alembic import op
import sqlalchemy as sa


revision = "d7e3f9a1b2c4"
down_revision = "c4f6a1e2b7d3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "medication_reminders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("configuring_clinician_id", sa.Integer(), nullable=False),
        sa.Column("medication_label_demo", sa.String(length=120), nullable=False),
        sa.Column("schedule_description", sa.String(length=240), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patient_profiles.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["configuring_clinician_id"], ["users.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_medication_reminders_patient_id",
        "medication_reminders",
        ["patient_id"],
    )
    op.create_index(
        "ix_medication_reminders_configuring_clinician_id",
        "medication_reminders",
        ["configuring_clinician_id"],
    )

    op.create_table(
        "medication_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("reminder_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("context", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patient_profiles.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["reminder_id"], ["medication_reminders.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_medication_events_patient_id", "medication_events", ["patient_id"]
    )
    op.create_index(
        "ix_medication_events_reminder_id", "medication_events", ["reminder_id"]
    )
    op.create_index(
        "ix_medication_events_recorded_at", "medication_events", ["recorded_at"]
    )


def downgrade():
    op.drop_index("ix_medication_events_recorded_at", table_name="medication_events")
    op.drop_index("ix_medication_events_reminder_id", table_name="medication_events")
    op.drop_index("ix_medication_events_patient_id", table_name="medication_events")
    op.drop_table("medication_events")
    op.drop_index(
        "ix_medication_reminders_configuring_clinician_id",
        table_name="medication_reminders",
    )
    op.drop_index("ix_medication_reminders_patient_id", table_name="medication_reminders")
    op.drop_table("medication_reminders")
