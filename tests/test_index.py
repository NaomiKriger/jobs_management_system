from http.client import OK


def test_index(test_client):
    response = test_client.get("/")
    assert response.status_code == OK
    json_response = response.get_json()
    assert json_response == {"message": "Welcome to the jobs management system!"}
    assert "Welcome to the jobs management system!" in response.text
