def test_invalid_incident_id():
    client = app.test_client()

    response = client.get('/api/incidents/999999')

    assert response.status_code == 404