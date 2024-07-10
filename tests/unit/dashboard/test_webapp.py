from fastapi.testclient import TestClient
from mandr.infomander import InfoMander


def test_index(client: TestClient):
    response = client.get("/")
    assert "html" in response.headers["Content-Type"]
    assert response.status_code == 200


def test_get_mandrs(client: TestClient):
    number_of_manders = 5
    for i in range(5):
        mander = InfoMander(f"probabl-ai/test-mandr/{i}")
        mander.add_info("hey", "ho")

    response = client.get("/mandrs")
    mander_paths = response.json()
    assert len(mander_paths) == number_of_manders
    assert response.status_code == 200
