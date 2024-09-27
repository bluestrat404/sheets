import json
import pytest
from src.app import app
from pathlib import Path

TEST_DATA_PATH = Path(__file__).parent / "data"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_html_endpoint(client):
    with open(TEST_DATA_PATH / "we-three-kings.chordpro", "r") as f:
        chord_pro_content = f.read()

    data = {
        "content": chord_pro_content,
        "transpose": 0
    }

    response = client.post('/generate_html', 
                           data=json.dumps(data),
                           content_type='application/json')

    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'html' in result
    assert 'error' in result
    assert 'Verdana' in result['html']
    assert 'We Three Kings Of Orient Are' in result['html']

def test_generate_pdf_endpoint(client):
    with open(TEST_DATA_PATH / "we-three-kings.chordpro", "r") as f:
        chord_pro_content = f.read()

    data = {
        "content": chord_pro_content,
        "transpose": 0
    }

    response = client.post('/generate_pdf', 
                           data=json.dumps(data),
                           content_type='application/json')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    assert response.headers['Content-Disposition'] == 'attachment; filename=generated_sheet.pdf'
    assert len(response.data) > 0

def test_invalid_request(client):
    data = {
        "content": "Invalid content"
        # Missing 'transpose' field
    }

    response = client.post('/generate_html', 
                           data=json.dumps(data),
                           content_type='application/json')

    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result

def test_rate_limiting(client):
    data = {
        "content": "Test content",
        "transpose": 0
    }

    # Make 11 requests to trigger rate limiting
    for _ in range(11):
        response = client.post('/generate_html', 
                               data=json.dumps(data),
                               content_type='application/json')

    assert response.status_code == 429  # Too Many Requests
