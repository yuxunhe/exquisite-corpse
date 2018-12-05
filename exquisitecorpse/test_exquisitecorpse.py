import os
import shutil
import tempfile

import pytest

from flask_migrate import init, migrate, upgrade

from exquisitecorpse import create_app, db, migrate


@pytest.fixture
def client():
    app = create_app()
    database_path = tempfile.mkstemp()
    app.config['DATABASE'] = "sql:///" + database_path[1]
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        upgrade()

    yield client

    os.close(database_path[0])
    os.unlink(database_path[1])


def login(client, username, password):
    return client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def register(client, username, password, repassword):
    return client.post('/auth/register', data=dict(
        username=username,
        password=password,
        re_entered_password=repassword
    ), follow_redirects=True)


def logout(client):
    return client.get('/auth/logout', follow_redirects=True)


def test_homepage(client):
    """Can we get to the homepage?"""
    rv = client.get('/')
    assert b'All corpses are completed! Please release a new corpse into the universe.' in rv.data


def test_register_login_logout(client):
    rv = register(client, 'test', 'testpass', 'testpass')
    assert b'You are now registered!' in rv.data
    rv = logout(client)
    assert b'Successfully logged out' in rv.data
    rv = login(client, 'test', 'testpass')
    assert b'Successfully logged in' in rv.data
    rv = logout(client)
    assert b'Successfully logged out' in rv.data
    

def test_bad_register(client):
    rv = register(client, None, None, None)
    assert b'Username is required' in rv.data
    assert b'Password is required' in rv.data
    logout(client)

    rv = register(client, None, 'testpass', 'testpass')
    assert b'Username is required' in rv.data
    logout(client)

    rv = register(client, 'test', None, 'testpass')
    assert b'Password is required' in rv.data
    assert b'Passwords do not match' in rv.data
    logout(client)

    rv = register(client, 'test', 'testpass', None)
    assert b'Passwords do not match' in rv.data
    logout(client)

    rv = register(client, None, None, 'testpass')
    assert b'Username is required' in rv.data
    assert b'Password is required' in rv.data
    assert b'Passwords do not match' in rv.data
    logout(client)

    rv = register(client, None, 'testpass', None)
    assert b'Username is required' in rv.data
    assert b'Passwords do not match' in rv.data
    logout(client)

    rv = register(client, 'test', None, None)
    assert b'Password is required' in rv.data
    logout(client)

    rv = register(client, 'test', 'testpass', 'nottestpass')
    assert b'Passwords do not match' in rv.data
    logout(client)


def test_bad_login(client):
    rv = register(client, 'test', 'testpass', 'testpass')
    rv = login(client, 'nottest', 'testpass')
    assert b'Incorrect username' in rv.data
    rv = login(client, 'test', 'nottestpass')
    assert b'Incorrect password' in rv.data


def test_bad_logout(client):
    pass

def test_double_register(client):
    rv = register(client, 'test', 'testpass', 'testpass')
    logout(client)
    rv = register(client, 'test', 'testpass', 'testpass')
    assert b'is already registered' in rv.data
