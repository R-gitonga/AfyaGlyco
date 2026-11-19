"""Central application rules for the AfyaGlyco demonstration prototype.

This module is the authoritative place for role permissions, ownership rules,
and shared field constraints. Routes and services must call these rules rather
than duplicating authorization decisions in templates or individual handlers.
"""

from datetime import timezone


CRUD_OPERATIONS = frozenset({"create", "read", "update", "delete"})

MEAL_TYPE_CHOICES = (
    ("breakfast", "Breakfast"),
    ("lunch", "Lunch"),
    ("dinner", "Dinner"),
    ("snack", "Snack"),
    ("other", "Other"),
)
MEAL_TYPES = frozenset(value for value, _label in MEAL_TYPE_CHOICES)
MEAL_DESCRIPTION_MAX_LENGTH = 500
EXERCISE_ACTIVITY_MAX_LENGTH = 120
EXERCISE_DURATION_MINUTES_MIN = 1
EXERCISE_DURATION_MINUTES_MAX = 1440
MEDICATION_LABEL_MAX_LENGTH = 120
REMINDER_SCHEDULE_MAX_LENGTH = 240
MEDICATION_EVENT_CONTEXT_MAX_LENGTH = 500
MEDICATION_EVENT_STATUS_CHOICES = (
    ("recorded", "Recorded"),
    ("skipped", "Skipped"),
    ("not_recorded", "Not recorded"),
)
MEDICATION_EVENT_STATUSES = frozenset(
    value for value, _label in MEDICATION_EVENT_STATUS_CHOICES
)
REPORT_DATE_FORMAT = "%Y-%m-%d"
REPORT_MAX_DATE_RANGE_DAYS = 366


RESOURCE_PERMISSIONS = {
    "user_account": {
        "administrator": frozenset({"create", "read", "update"}),
    },
    "patient_profile": {
        "patient": frozenset({"read", "update"}),
        "clinician": frozenset({"read"}),
        "administrator": frozenset({"read"}),
    },
    "glucose_reading": {
        "patient": CRUD_OPERATIONS,
        "clinician": frozenset({"read"}),
    },
    "meal_log": {
        "patient": CRUD_OPERATIONS,
        "clinician": frozenset({"read"}),
    },
    "exercise_log": {
        "patient": CRUD_OPERATIONS,
        "clinician": frozenset({"read"}),
    },
    "clinician_note": {
        "patient": frozenset({"read"}),
        "clinician": frozenset({"create", "read"}),
    },
    "medication_reminder": {
        "patient": frozenset({"read"}),
        "clinician": CRUD_OPERATIONS,
    },
    "medication_event": {
        "patient": CRUD_OPERATIONS,
        "clinician": frozenset({"read"}),
    },
    "patient_report": {
        "patient": frozenset({"read"}),
        "clinician": frozenset({"read"}),
    },
}


def allowed_operations(resource, role_name):
    """Return the operations a role may perform on a resource."""
    return RESOURCE_PERMISSIONS.get(resource, {}).get(role_name, frozenset())


def can_perform(user, resource, operation, *, patient_profile=None):
    """Check role and record scope for an application operation.

    Patient-owned resources require the supplied profile to belong to the
    signed-in patient. Clinician reads require the profile to be assigned to
    that clinician. Administrators do not receive health-record access by
    default; their permissions are limited to the resources listed above.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if not getattr(user, "is_active", False):
        return False
    if operation not in CRUD_OPERATIONS:
        return False

    for role in getattr(user, "roles", ()):
        if operation not in allowed_operations(resource, role.name):
            continue
        if role.name == "patient":
            return patient_profile is not None and patient_profile.user_id == user.id
        if role.name == "clinician":
            return (
                patient_profile is not None
                and patient_profile.assigned_clinician_id == user.id
            )
        return True
    return False


def can_change_account_status(actor, target):
    """Prevent an administrator from locking their own account."""
    return (
        actor is not None
        and target is not None
        and actor.is_active
        and actor.has_role("administrator")
        and actor.id != target.id
    )


def normalize_recorded_at(value):
    """Return a timezone-aware value for storage without interpreting it."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
