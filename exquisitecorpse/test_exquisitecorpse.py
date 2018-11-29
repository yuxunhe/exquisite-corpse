import os
import shutil
import tempfile

import pytest

from exquisitecorpse import create_app


@pytest.fixture
def client():
    app = create_app()
    database_path = tempfile.mkstemp()
    app.config['DATABASE'] = "sql:///" + database_path[1]
    app.config['TESTING'] = True
    migration_dir = tempfile.mkdtemp()
    client = app.test_client()

    with app.app_context():
        app.migrate.init(directory=migration_dir)
        app.migrate.migrate(directory=migration_dir)
        app.migrate.upgrade(directory=migration_dir)

    yield client

    os.close(database_path)
    os.unlink(database_path)
    shutil.rmtree(migration_dir)
