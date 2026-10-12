import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def api(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app), activities


def test_registers_student_for_activity(api):
    # Arrange
    client, activities = api
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_rejects_duplicate_registration(api):
    # Arrange
    client, activities = api
    participants_before = activities["Chess Club"]["participants"].copy()

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities["Chess Club"]["participants"] == participants_before


def test_rejects_registration_for_invalid_activity(api):
    # Arrange
    client, activities = api
    participants_before = activities["Chess Club"]["participants"].copy()

    # Act
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "new@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert activities["Chess Club"]["participants"] == participants_before


def test_unregisters_student_from_activity(api):
    # Arrange
    client, activities = api
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_rejects_unregistering_from_invalid_activity(api):
    # Arrange
    client, activities = api
    participants_before = activities["Chess Club"]["participants"].copy()

    # Act
    response = client.delete(
        "/activities/Unknown Activity/participants",
        params={"email": "existing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert activities["Chess Club"]["participants"] == participants_before


def test_rejects_unregistering_student_not_in_activity(api):
    # Arrange
    client, activities = api
    participants_before = activities["Chess Club"]["participants"].copy()

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "not-registered@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activities["Chess Club"]["participants"] == participants_before
