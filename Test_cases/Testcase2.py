def test_list_incidents_endpoint():
    client = app.test_client()

    response = client.get('/api/incidents')

    assert response.status_code == 200