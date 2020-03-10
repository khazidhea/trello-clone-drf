from django.db import models
from django.core.exceptions import PermissionDenied
from django_fsm import FSMField, transition, TransitionNotAllowed, has_transition_perm
from rules import predicate
from rules.contrib.models import RulesModel


@predicate
def is_task_assignee(user, task):
    if user and task:
        return task.assignee == user
    return False


@predicate
def is_task_author(user, task):
    if user and task:
        return task.author == user
    return False


@predicate
def is_user_superuser(user):
    return user.is_superuser


class Task(RulesModel):
    class Meta:
        rules_permissions = {
            'can_complete': is_task_assignee,
            'can_request_changes': is_task_author,
            'can_close': is_user_superuser,
        }

    STATUS_NEW = 'new'
    STATUS_PENDING = 'pending approval'
    STATUS_INPROGRESS = 'in progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CHANGES_REQUESTED = 'changes requested'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = (
        (STATUS_NEW, STATUS_NEW),
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_INPROGRESS, STATUS_INPROGRESS),
        (STATUS_COMPLETED, STATUS_COMPLETED),
        (STATUS_CHANGES_REQUESTED, STATUS_CHANGES_REQUESTED),
        (STATUS_CLOSED, STATUS_CLOSED),
    )

    author = models.ForeignKey('users.User', related_name='tasks_authored', on_delete=models.CASCADE)
    assignee = models.ForeignKey('users.User', related_name='tasks_assigned', on_delete=models.CASCADE)
    approvers = models.ManyToManyField('users.User', related_name='tasks_for_approval', through='Approval')
    title = models.CharField(max_length=200)
    status = FSMField(default=STATUS_NEW, choices=STATUS_CHOICES, protected=True)

    def transition_with_permission(self, method, user):
        if has_transition_perm(method, user):
            method()
        else:
            raise PermissionDenied

    @transition(field=status, source=STATUS_NEW, target=STATUS_PENDING)
    def to_status_pending(self):
        pass

    def approve(self, user):
        try:
            approval = Approval.objects.get(approver=user, task=self)
        except Approval.DoesNotExist:
            raise PermissionDenied
        approval.is_approved = True
        approval.save()
        try:
            self.to_status_inprogress()
        except TransitionNotAllowed:
            pass

    @transition(
        field=status, source=STATUS_PENDING, target=STATUS_INPROGRESS,
        conditions=[
            lambda instance: all(
                Approval.objects.filter(task=instance).values_list('is_approved', flat=True)
            )
        ]
    )
    def to_status_inprogress(self):
        pass

    def complete(self, user):
        self.transition_with_permission(self.to_status_completed, user)

    @transition(
        field=status,
        source=[STATUS_INPROGRESS, STATUS_CHANGES_REQUESTED], target=STATUS_COMPLETED,
        permission='tasks.can_complete_task'
    )
    def to_status_completed(self):
        pass

    def request_changes(self, user):
        self.transition_with_permission(self.to_status_changes_requested, user)

    @transition(
        field=status,
        source=STATUS_COMPLETED, target=STATUS_CHANGES_REQUESTED,
        permission='tasks.can_request_changes_task'
    )
    def to_status_changes_requested(self):
        pass

    def close(self, user):
        self.transition_with_permission(self.to_status_closed, user)

    @transition(
        field=status,
        source='*', target=STATUS_CLOSED,
        permission='tasks.can_close_task'
    )
    def to_status_closed(self):
        pass

    def pending_approvers(self):
        return [approval.approver for approval in Approval.objects.filter(task=self, is_approved=False)]


class Approval(models.Model):
    approver = models.ForeignKey(
        'users.User', related_name='approvals', on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        'tasks.Task', related_name='approvals', on_delete=models.CASCADE
    )
    is_approved = models.BooleanField(default=False)
