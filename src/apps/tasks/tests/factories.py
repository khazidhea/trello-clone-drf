import factory

from src.apps.users.tests.factories import UserFactory
from ..models import Task


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    author = factory.SubFactory(UserFactory)
    assignee = factory.SubFactory(UserFactory)
    title = factory.Faker('text')

    @staticmethod
    def pending():
        task = TaskFactory()
        user = UserFactory()
        task.approvers.add(user)
        return task

    @staticmethod
    def inprogress():
        task = TaskFactory()
        for user in UserFactory.create_batch(3):
            task.approvers.add(user) 
            task.approve(user)
        return task

    @staticmethod
    def completed():
        task = TaskFactory.inprogress()
        task.complete(task.assignee)
        return task

    @staticmethod
    def changes_requested():
        task = TaskFactory.completed()
        task.request_changes(task.author)
        return task
