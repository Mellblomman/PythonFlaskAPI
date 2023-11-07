import base64
import json
import os
import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def mock_open_function():
    with patch('builtins.open', create=True) as mock_open:
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = json.dumps({"tasks": []})
        yield mock_open


def test_get_tasks(mock_open_function):
    response = app.test_client().get('/')
    assert response.status_code == 500


def test_get_filtered_tasks(mock_open_function, client):
    response = client.get('/tasks')
    assert response.status_code == 200


def test_post_task(mock_open_function, client):
    data = {
        "description": "Test task",
        "category": "Test category"
    }
    response = client.post('/tasks', data=data)
    assert response.status_code in (200, 302)  # 200 for JSON response, 302 for redirect


def test_get_task(mock_open_function, client):
    response = client.get('/tasks/1')
    assert response.status_code == 404


def test_delete_task(mock_open_function, client):
    credentials = base64.b64encode(b'my_user:password').decode('utf-8')
    headers = {
        'Authorization': 'Basic ' + credentials
    }

    response = client.delete('/tasks/1', headers=headers)
    assert response.status_code == 401


def test_update_task(mock_open_function, client):
    data = {
        "description": "Updated test task",
        "category": "Updated test category"
    }
    response = client.put('/tasks/1', json=data)
    assert response.status_code == 404


def test_complete_task(mock_open_function, client):
    response = client.put('/tasks/1/complete')
    assert response.status_code == 404


def test_get_all_categories(mock_open_function, client):
    response = client.get('/tasks/categories')
    assert response.status_code == 200


def test_get_tasks_by_category(mock_open_function, client):
    response = client.get('/tasks/categories/Test')
    assert response.status_code == 200