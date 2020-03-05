import factory

from src.apps.users.tests.factories import UserFactory
from ..models import Task


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    author = factory.SubFactory(UserFactory)
    assignee = factory.SubFactory(UserFactory)
    title = factory.Faker('text')
