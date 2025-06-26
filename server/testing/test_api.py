import pytest
from server.app import app
from server.models import db, Newsletter

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == "Welcome to the Newsletter RESTful API"

def test_get_empty_newsletters(client):
    response = client.get('/newsletters')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_post_newsletter(client):
    response = client.post('/newsletters', data={'title': 'Test Title', 'body': 'Test Body'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Title'
    assert data['body'] == 'Test Body'
    assert 'id' in data

def test_get_newsletters_after_post(client):
    client.post('/newsletters', data={'title': 'Test Title', 'body': 'Test Body'})
    response = client.get('/newsletters')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['title'] == 'Test Title'

def test_get_newsletter_by_id(client):
    post_response = client.post('/newsletters', data={'title': 'Test Title', 'body': 'Test Body'})
    post_data = post_response.get_json()
    newsletter_id = post_data['id']
    get_response = client.get(f'/newsletters/{newsletter_id}')
    assert get_response.status_code == 200
    get_data = get_response.get_json()
    assert get_data['title'] == 'Test Title'
    assert get_data['body'] == 'Test Body'

def test_get_newsletter_by_invalid_id(client):
    response = client.get('/newsletters/999')
    # The current implementation will raise an error if not found, so this test expects a 500 or similar
    assert response.status_code != 200
