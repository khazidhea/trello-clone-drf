import factory

from src.apps.users.tests.factories import UserFactory
from ..models import Task
from ..services import TaskService


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    author = factory.SubFactory(UserFactory)
    assignee = factory.SubFactory(UserFactory)
    title = factory.Faker('text')

    @staticmethod
    def pending():
        task = TaskFactory()
        approver = UserFactory()
        TaskService(task).add_approver(approver)
        return task

    @staticmethod
    def inprogress():
        task = TaskFactory()
        task_service = TaskService(task)
        for user in UserFactory.create_batch(3):
            task_service.add_approver(user)
            task_service.approve(user.id)
        return task

    @staticmethod
    def completed():
        task = TaskFactory.inprogress()
        TaskService(task).complete(task.assignee.id)
        return task

    @staticmethod
    def changes_requested():
        task = TaskFactory.completed()
        TaskService(task).request_changes(task.author.id)
        return task
