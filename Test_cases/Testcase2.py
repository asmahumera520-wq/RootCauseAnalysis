from app import app

def test_generate_rca_missing_title():
    client = app.test_client()

    response = client.post('/api/generate-rca', data={
        "title": "",
        "timeline": "02:15 Alert triggered"
    })

    assert response.status_code == 400
