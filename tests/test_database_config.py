import os
import unittest
from unittest.mock import patch

from app.database_config import database_diagnostic, get_database_url


class DatabaseConfigTests(unittest.TestCase):
    def test_legacy_postgres_scheme_is_normalized(self):
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgres://user:secret@db.internal:5432/banking"},
            clear=True,
        ):
            self.assertEqual(
                get_database_url(),
                "postgresql://user:secret@db.internal:5432/banking",
            )

    def test_external_render_url_uses_tls_when_not_specified(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": (
                    "postgresql://user:secret@"
                    "dpg-example.oregon-postgres.render.com/banking"
                )
            },
            clear=True,
        ):
            self.assertIn("sslmode=require", get_database_url())

    def test_diagnostic_never_includes_password(self):
        database_url = "postgresql://user:secret@dpg-example/banking"

        diagnostic = database_diagnostic(database_url)

        self.assertIn("source=DATABASE_URL", diagnostic)
        self.assertIn("host=dpg-example", diagnostic)
        self.assertNotIn("secret", diagnostic)
        self.assertNotIn("user@", diagnostic)


if __name__ == "__main__":
    unittest.main()
