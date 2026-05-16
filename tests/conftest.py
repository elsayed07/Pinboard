import pytest
from django.test import Client

from tests.factories.accounts import UserFactory


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client
