from django.contrib.auth.models import AbstractUser
from django_fsm import TransitionNotAllowed

from src.apps.tasks.models import Approval


class User(AbstractUser):
    def approve(self, task):
        approval = Approval.objects.get(approver=self, task=task)
        approval.is_approved=True
        approval.save()
        try:
            task.to_status_inprogress()
        except TransitionNotAllowed:
            pass

    def complete(self, task):
        if task.assignee == self:
            task.to_status_completed()

    def request_changes(self, task):
        if task.author == self:
            task.to_status_changes_requested()

    def close(self, task):
        if self.is_superuser:
            task.to_status_closed()
