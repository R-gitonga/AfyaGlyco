from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


role_assignments = db.Table(
    "role_assignments",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    roles = db.relationship(
        "Role",
        secondary=role_assignments,
        back_populates="users",
    )
    patient_profile = db.relationship(
        "PatientProfile",
        foreign_keys="PatientProfile.user_id",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    assigned_patients = db.relationship(
        "PatientProfile",
        foreign_keys="PatientProfile.assigned_clinician_id",
        back_populates="assigned_clinician",
    )
    authored_notes = db.relationship(
        "ClinicianNote",
        foreign_keys="ClinicianNote.author_user_id",
        back_populates="author",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    users = db.relationship(
        "User",
        secondary=role_assignments,
        back_populates="roles",
    )


class PatientProfile(db.Model):
    __tablename__ = "patient_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    assigned_clinician_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    display_name = db.Column(db.String(120), nullable=False)
    date_of_birth_demo = db.Column(db.Date, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="patient_profile",
    )
    assigned_clinician = db.relationship(
        "User",
        foreign_keys=[assigned_clinician_id],
        back_populates="assigned_patients",
    )
    glucose_readings = db.relationship(
        "GlucoseReading",
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="GlucoseReading.recorded_at.desc()",
    )
    clinician_notes = db.relationship(
        "ClinicianNote",
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="ClinicianNote.created_at.desc()",
    )


class GlucoseReading(db.Model):
    __tablename__ = "glucose_readings"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    value_demo = db.Column(db.Numeric(8, 2), nullable=False)
    recorded_at = db.Column(db.DateTime(timezone=True), nullable=False)
    reading_context = db.Column(db.String(80), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    patient = db.relationship("PatientProfile", back_populates="glucose_readings")


class ClinicianNote(db.Model):
    __tablename__ = "clinician_notes"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    patient = db.relationship("PatientProfile", back_populates="clinician_notes")
    author = db.relationship(
        "User",
        foreign_keys=[author_user_id],
        back_populates="authored_notes",
    )
