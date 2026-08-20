"""Database URL loading and diagnostics shared by the application and Alembic."""

import os

from sqlalchemy.engine import make_url


DATABASE_URL_ENV_VAR = "DATABASE_URL"


def get_database_url() -> str:
    """Return the configured PostgreSQL URL without logging its credentials."""
    database_url = os.getenv(DATABASE_URL_ENV_VAR)
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is missing. Configure it with the "
            "current Render PostgreSQL connection URL."
        )

    # Render and some older hosting integrations provide this legacy scheme.
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://") :]

    url = make_url(database_url)
    if not url.drivername.startswith("postgresql"):
        raise RuntimeError("DATABASE_URL must contain a PostgreSQL connection URL.")

    query = dict(url.query)
    # Render's external hostname requires TLS. Its internal URL must be left
    # unchanged so a same-region private-network connection continues to work.
    if url.host and url.host.endswith(".render.com") and "sslmode" not in query:
        query["sslmode"] = "require"

    return url.set(query=query).render_as_string(hide_password=False)


def database_diagnostic(database_url: str) -> str:
    """Return safe connection metadata for startup logs; never include secrets."""
    url = make_url(database_url)
    if url.host and url.host.endswith(".render.com"):
        network = "Render external"
    elif url.host and url.host.startswith("dpg-"):
        network = "Render internal"
    else:
        network = "non-Render or local"

    sslmode = url.query.get("sslmode", "not set")
    return (
        f"source={DATABASE_URL_ENV_VAR}, network={network}, host={url.host}, "
        f"port={url.port or 5432}, database={url.database}, sslmode={sslmode}"
    )
