def test_board_page_loads_as_html(client):
    response = client.get("/board")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_board_page_starts_on_the_default_window_and_uses_the_availability_endpoint(client):
    page = client.get("/board").text

    assert 'value="2026-12-31T09:00"' in page
    assert 'value="2026-12-31T12:00"' in page
    assert "/heroes/available" in page
