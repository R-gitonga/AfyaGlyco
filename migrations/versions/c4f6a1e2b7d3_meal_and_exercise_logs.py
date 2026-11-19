"""Add patient meal and exercise logs.

Revision ID: c4f6a1e2b7d3
Revises: 8b2c7d9e4f10
"""

from alembic import op
import sqlalchemy as sa


revision = "c4f6a1e2b7d3"
down_revision = "8b2c7d9e4f10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "meal_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("meal_type", sa.String(length=30), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patient_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_meal_logs_patient_id",
        "meal_logs",
        ["patient_id"],
    )
    op.create_index(
        "ix_meal_logs_recorded_at",
        "meal_logs",
        ["recorded_at"],
    )

    op.create_table(
        "exercise_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("activity_type", sa.String(length=120), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patient_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "duration_minutes > 0",
            name="ck_exercise_logs_duration_positive",
        ),
    )
    op.create_index(
        "ix_exercise_logs_patient_id",
        "exercise_logs",
        ["patient_id"],
    )
    op.create_index(
        "ix_exercise_logs_recorded_at",
        "exercise_logs",
        ["recorded_at"],
    )


def downgrade():
    op.drop_index("ix_exercise_logs_recorded_at", table_name="exercise_logs")
    op.drop_index("ix_exercise_logs_patient_id", table_name="exercise_logs")
    op.drop_table("exercise_logs")
    op.drop_index("ix_meal_logs_recorded_at", table_name="meal_logs")
    op.drop_index("ix_meal_logs_patient_id", table_name="meal_logs")
    op.drop_table("meal_logs")
