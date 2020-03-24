from functools import wraps

from django.core.exceptions import PermissionDenied

from transitions import Machine, MachineError

from src.apps.users.models import User
from .models import Task, Approval


def is_assignee(task: Task, user_id: int) -> bool:
    return task.assignee.id == user_id


def is_author(task: Task, user_id: int) -> bool:
    return task.author.id == user_id


def is_superuser(task: Task, user_id: int) -> bool:
    return User.objects.get(id=user_id).is_superuser


def permission_decorator(check):
    def decorator(fn):
        @wraps(fn)
        def permission_wrapper(*args, **kwargs):
            instance = args[0]
            user_id = args[1]
            if check(instance.task, user_id):
                return fn(*args, **kwargs)
            else:
                raise PermissionDenied
        return permission_wrapper
    return decorator


class TaskService:
    def __init__(self, task: Task):
        self.task = task
        states = [status[0] for status in Task.STATUS_CHOICES]
        self.machine = Machine(
            model=self,
            states=states,
            initial=self.task.status,
            auto_transitions=False,
            after_state_change='save',
        )
        self.machine.add_transition(
            trigger='to_pending',
            source=Task.STATUS_NEW,
            dest=Task.STATUS_PENDING
        )
        self.machine.add_transition(
            trigger='to_inprogress',
            source=Task.STATUS_PENDING,
            dest=Task.STATUS_INPROGRESS,
            conditions=['is_approved']
        )
        self.machine.add_transition(
            trigger='to_completed',
            source=[Task.STATUS_INPROGRESS, Task.STATUS_CHANGES_REQUESTED],
            dest=Task.STATUS_COMPLETED
        )
        self.machine.add_transition(
            trigger='to_changes_requested',
            source=Task.STATUS_COMPLETED,
            dest=Task.STATUS_CHANGES_REQUESTED
        )
        self.machine.add_transition(
            trigger='to_closed',
            source='*',
            dest=Task.STATUS_CLOSED
        )

    def save(self) -> None:
        self.task.status = self.state
        self.task.save()

    def is_approved(self) -> bool:
        return all(Approval.objects.filter(task=self.task).values_list('is_approved', flat=True))

    @permission_decorator(is_assignee)
    def complete(self, user_id: int) -> None:
        self.to_completed()

    @permission_decorator(is_author)
    def request_changes(self, user_id: int) -> None:
        self.to_changes_requested()

    @permission_decorator(is_superuser)
    def close(self, user_id: int) -> None:
        self.to_closed()

    def add_approver(self, user_id: int) -> None:
        self.task.approvers.add(user_id)
        if self.task.status == Task.STATUS_NEW:
            self.to_pending()

    def approve(self, user_id: int) -> Approval:
        try:
            approval = Approval.objects.get(approver_id=user_id, task=self.task)
        except Approval.DoesNotExist:
            raise PermissionDenied
        approval.is_approved = True
        approval.save()
        try:
            self.to_inprogress()
        except MachineError:
            pass
        return approval
