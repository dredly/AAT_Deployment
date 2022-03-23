# Sample code from offical Flask tutorial:
# https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
# Not implemented yet as no create_app functionality in aat at time of writing
# - Rich, 11th March 2022

###########################################

import os, tempfile, pytest
from aat import create_app
from aat.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
