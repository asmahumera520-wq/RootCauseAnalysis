from app import app

def test_generate_rca_missing_timeline():
    client = app.test_client()

    response = client.post('/api/generate-rca', data={
        "title": "Payment API Outage",
        "timeline": ""
    })

    assert response.status_code == 400
