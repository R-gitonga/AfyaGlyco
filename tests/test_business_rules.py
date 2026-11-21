"""Unit tests for centralized permission and ownership decisions."""

from types import SimpleNamespace

from app.business_rules import (
    allowed_operations,
    can_change_account_status,
    can_perform,
)


def user(user_id, role_name, active=True):
    return SimpleNamespace(
        id=user_id,
        is_active=active,
        is_authenticated=True,
        roles=[SimpleNamespace(name=role_name)],
        has_role=lambda name: name == role_name,
    )


def test_business_rules_expose_complete_meal_and_exercise_crud_matrix():
    assert allowed_operations("meal_log", "patient") == {
        "create",
        "read",
        "update",
        "delete",
    }
    assert allowed_operations("exercise_log", "patient") == {
        "create",
        "read",
        "update",
        "delete",
    }
    assert allowed_operations("meal_log", "clinician") == {"read"}
    assert allowed_operations("exercise_log", "clinician") == {"read"}


def test_business_rules_expose_medication_crud_matrix():
    assert allowed_operations("medication_reminder", "clinician") == {
        "create",
        "read",
        "update",
        "delete",
    }
    assert allowed_operations("medication_reminder", "patient") == {"read"}
    assert allowed_operations("medication_event", "patient") == {
        "create",
        "read",
        "update",
        "delete",
    }
    assert allowed_operations("medication_event", "clinician") == {"read"}


def test_business_rules_keep_reports_read_only():
    assert allowed_operations("patient_report", "patient") == {"read"}
    assert allowed_operations("patient_report", "clinician") == {"read"}
    assert allowed_operations("patient_report", "administrator") == set()


def test_business_rules_expose_organization_and_registration_boundaries():
    assert allowed_operations("organization", "administrator") == {
        "create",
        "read",
        "update",
    }
    assert allowed_operations("clinician_account", "administrator") == {
        "create",
        "read",
        "update",
    }
    assert allowed_operations("patient_registration", "clinician") == {
        "create",
        "read",
        "update",
    }
    assert allowed_operations("patient_assignment", "clinician") == {
        "create",
        "read",
    }
    assert allowed_operations("patient_assignment", "administrator") == {
        "create",
        "read",
        "update",
    }


def test_business_rules_enforce_patient_ownership_and_clinician_assignment():
    patient = user(1, "patient")
    clinician = user(2, "clinician")
    own_profile = SimpleNamespace(user_id=1, assigned_clinician_id=2)
    other_profile = SimpleNamespace(user_id=3, assigned_clinician_id=2)

    assert can_perform(
        patient, "meal_log", "update", patient_profile=own_profile
    )
    assert not can_perform(
        patient, "meal_log", "update", patient_profile=other_profile
    )
    assert can_perform(
        clinician, "exercise_log", "read", patient_profile=own_profile
    )
    assert not can_perform(
        clinician, "exercise_log", "delete", patient_profile=own_profile
    )


def test_business_rules_prevent_administrator_self_lockout():
    administrator = user(1, "administrator")
    other_user = user(2, "patient")

    assert not can_change_account_status(administrator, administrator)
    assert can_change_account_status(administrator, other_user)
