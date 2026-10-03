"""Tests for user authentication and progressive registration."""
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_user_registration_and_token():
    client = APIClient()
    payload = {
        "email": "new.supplier@btp-dz.com",
        "password": "PasswordSecure2026!",
        "full_name": "مراد طاهري",
        "phone": "+213550123456",
        "role": "ECONOMIC_OPERATOR_ADMIN",
        "org_name": "مؤسسة طاهري للمقاولات",
        "org_type": "ECONOMIC_OPERATOR",
        "nif": "002016009876543"
    }
    response = client.post("/api/v1/auth/register/", payload, format="json")
    assert response.status_code == 201
    assert "token" in response.data
    assert response.data["user"]["email"] == "new.supplier@btp-dz.com"
    assert response.data["user"]["organization_name"] == "مؤسسة طاهري للمقاولات"

@pytest.mark.django_db
def test_user_login_success(officer_user):
    client = APIClient()
    response = client.post("/api/v1/auth/login/", {
        "email": officer_user.email,
        "password": "ValidStrongPassword2026!"
    }, format="json")
    assert response.status_code == 200
    assert "token" in response.data
    assert response.data["user"]["id"] == str(officer_user.id)

@pytest.mark.django_db
def test_user_login_invalid_credentials():
    client = APIClient()
    response = client.post("/api/v1/auth/login/", {
        "email": "wrong@user.dz",
        "password": "WrongPassword!"
    }, format="json")
    assert response.status_code == 400
    assert "error" in response.data
