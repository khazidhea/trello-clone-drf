from pytest_factoryboy import register

from .tasks.tests.factories import TaskFactory
from .users.tests.factories import UserFactory


register(TaskFactory)
register(UserFactory)
