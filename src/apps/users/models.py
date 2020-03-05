from django.contrib.auth.models import AbstractUser

from src.apps.tasks.models import Approval


class User(AbstractUser):
    def request_changes(self, task):
        if task.author == self:
            task.to_status_changes_requested()

    def close(self, task):
        if self.is_superuser:
            task.to_status_closed()
