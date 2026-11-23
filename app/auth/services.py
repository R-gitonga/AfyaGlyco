"""Authentication services, including the first-administrator bootstrap."""

from sqlalchemy import select, text

from app import db
from app.models import Role, User


ADMINISTRATOR_ROLE = "administrator"


class BootstrapUnavailable(Exception):
    """Raised when the one-time administrator bootstrap is already closed."""


def bootstrap_available():
    """Return whether the database currently has no user accounts."""

    return db.session.scalar(select(User.id).limit(1)) is None


def create_initial_administrator(email, display_name, password):
    """Create the first administrator while serializing PostgreSQL requests."""

    # An empty-table check alone can race when two public requests arrive at the
    # same time. PostgreSQL's table lock makes the check-and-create operation
    # one-time for the deployment database; SQLite tests use its transaction lock.
    if db.engine.dialect.name == "postgresql":
        db.session.execute(text("LOCK TABLE users IN SHARE ROW EXCLUSIVE MODE"))

    if not bootstrap_available():
        raise BootstrapUnavailable

    role = db.session.scalar(
        select(Role).where(Role.name == ADMINISTRATOR_ROLE)
    )
    if role is None:
        role = Role(name=ADMINISTRATOR_ROLE)
        db.session.add(role)

    administrator = User(
        email=email.strip().lower(),
        display_name=display_name.strip(),
    )
    administrator.set_password(password)
    administrator.roles.append(role)
    db.session.add(administrator)
    db.session.commit()
    return administrator
