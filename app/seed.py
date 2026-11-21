"""Create repeatable fictional roles, organizations, and demonstration accounts."""

import secrets

import click

from app import db
from app.models import Organization, PatientProfile, Role, User


DEMO_ACCOUNTS = {
    "patient": "patient@example.test",
    "clinician": "clinician@example.test",
    "administrator": "admin@example.test",
}


def _get_or_create_role(role_name):
    role = Role.query.filter_by(name=role_name).first()
    if role is None:
        role = Role(name=role_name)
        db.session.add(role)
    return role


def _get_or_create_organization():
    organization = Organization.query.filter_by(
        name="AfyaGlyco Demo Clinic"
    ).first()
    if organization is None:
        organization = Organization(
            name="AfyaGlyco Demo Clinic",
            organization_type="clinic",
        )
        db.session.add(organization)
    organization.is_active = True
    return organization


def _get_or_create_user(email, role, password, reset_password=False):
    user = User.query.filter_by(email=email).first()
    created = user is None
    if created:
        user = User(email=email)
        db.session.add(user)

    user.is_active = True
    if created or reset_password:
        user.set_password(password)
    if role not in user.roles:
        user.roles.append(role)
    return user, created


def register_seed_command(app):
    @app.cli.command("seed-demo")
    @click.option(
        "--password",
        envvar="DEMO_SEED_PASSWORD",
        help="Password to use for newly created demo accounts.",
    )
    def seed_demo(password):
        """Create or refresh fictional accounts for the demonstration."""
        generated_password = password or secrets.token_urlsafe(12)
        roles = {
            name: _get_or_create_role(name) for name in DEMO_ACCOUNTS
        }
        organization = _get_or_create_organization()
        users = {}
        created_accounts = []
        for role_name, email in DEMO_ACCOUNTS.items():
            user, created = _get_or_create_user(
                email,
                roles[role_name],
                generated_password,
                reset_password=password is not None,
            )
            users[role_name] = user
            if created:
                created_accounts.append(email)

        users["clinician"].organization = organization
        users["clinician"].display_name = users["clinician"].display_name or "Demo Clinician"
        users["patient"].organization = organization

        patient_profile = PatientProfile.query.filter_by(
            user_id=users["patient"].id
        ).first()
        if patient_profile is None:
            patient_profile = PatientProfile(
                user=users["patient"],
                assigned_clinician=users["clinician"],
                organization=organization,
                display_name="Demo Patient",
            )
            db.session.add(patient_profile)
        else:
            patient_profile.assigned_clinician = users["clinician"]
            patient_profile.organization = organization

        db.session.commit()

        click.echo("Fictional demo accounts are ready:")
        for role_name, email in DEMO_ACCOUNTS.items():
            click.echo(f"  {role_name}: {email}")
        if created_accounts or password:
            click.echo(f"  password: {generated_password}")
        else:
            click.echo(
                "  existing passwords were preserved; use --password to reset them."
            )
