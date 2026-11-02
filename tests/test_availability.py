import pytest

from heroes_api.db import HEROES

WINDOW = {"start": "2026-09-14T09:00", "end": "2026-09-14T12:00"}


def book(client, client_id, hero, start, end):
    response = client.post(
        "/bookings",
        json={"client_id": client_id, "hero": hero, "start": start, "end": end, "mission": "Market patrol"},
    )
    assert response.status_code == 201
    return response


def available(client, params=WINDOW):
    return client.get("/heroes/available", params=params)


def test_with_no_bookings_every_hero_is_free_in_roster_order(client):
    response = available(client)

    assert response.status_code == 200
    assert response.json() == [{"name": name, "power": power} for name, power in HEROES]


def test_a_hero_booked_inside_the_window_is_not_free(client, harbour_council):
    book(client, harbour_council["id"], "Brisk", "2026-09-14T10:00", "2026-09-14T11:00")

    names = [h["name"] for h in available(client).json()]

    assert "Brisk" not in names
    assert len(names) == 14


@pytest.mark.parametrize(
    "start, end",
    [
        ("2026-09-14T08:00", "2026-09-14T10:00"),
        ("2026-09-14T11:00", "2026-09-14T13:00"),
        ("2026-09-14T07:00", "2026-09-14T14:00"),
    ],
    ids=["straddles-start", "straddles-end", "covers-window"],
)
def test_a_hero_booked_for_part_of_the_window_is_not_free(client, harbour_council, start, end):
    book(client, harbour_council["id"], "Brisk", start, end)

    names = [h["name"] for h in available(client).json()]

    assert "Brisk" not in names


@pytest.mark.parametrize(
    "start, end",
    [
        ("2026-09-14T06:00", "2026-09-14T09:00"),
        ("2026-09-14T12:00", "2026-09-14T15:00"),
        ("2026-09-15T09:00", "2026-09-15T12:00"),
    ],
    ids=["ends-at-window-start", "starts-at-window-end", "another-day"],
)
def test_a_booking_that_does_not_overlap_leaves_the_hero_free(client, harbour_council, start, end):
    book(client, harbour_council["id"], "Brisk", start, end)

    names = [h["name"] for h in available(client).json()]

    assert "Brisk" in names
    assert len(names) == 15


@pytest.mark.parametrize(
    "params",
    [
        {"start": "2026-09-14T12:00", "end": "2026-09-14T09:00"},
        {"start": "2026-09-14T09:00", "end": "2026-09-14T09:00"},
        {"start": "2026-09-14T09:00"},
        {"start": "2026-09-14T09:00+01:00", "end": "2026-09-14T12:00"},
    ],
    ids=["end-before-start", "end-equals-start", "missing-end", "time-zone"],
)
def test_an_invalid_window_returns_422(client, params):
    response = available(client, params)

    assert response.status_code == 422
