from django.db import models
from django_fsm import FSMField, transition


class Task(models.Model):
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

    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    assignee = models.ForeignKey('users.User', on_delete=models.CASCADE)
    approvers = models.ManyToManyField('users.User', through='Approval')
    title = models.CharField(max_length=200)
    status = FSMField(default=STATUS_NEW, choices=STATUS_CHOICES, protected=True)

    @transition(field=status, source=STATUS_NEW, target=STATUS_PENDING)
    def to_status_pending(self):
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

    @transition(field=status, source=[STATUS_INPROGRESS, STATUS_CHANGES_REQUESTED], target=STATUS_COMPLETED)
    def to_status_completed(self):
        pass

    @transition(field=status, source=STATUS_COMPLETED, target=STATUS_CHANGES_REQUESTED)
    def to_status_changes_requested(self):
        pass

    @transition(field=status, source='*', target=STATUS_CLOSED)
    def to_status_closed(self):
        pass

    def pending_approvers(self):
        return [approval.approver for approval in Approval.objects.filter(task=self, is_approved=False)]


class Approval(models.Model):
    approver = models.ForeignKey('users.User', on_delete=models.CASCADE)
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
