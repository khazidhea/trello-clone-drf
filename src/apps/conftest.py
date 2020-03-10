import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from .tasks.tests.factories import TaskFactory
from .users.tests.factories import UserFactory


register(TaskFactory)
register(UserFactory)


@pytest.fixture
def client():
    return APIClient()
