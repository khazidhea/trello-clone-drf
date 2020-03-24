from django.db import models


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

    author = models.ForeignKey('users.User', related_name='tasks_authored', on_delete=models.CASCADE)
    assignee = models.ForeignKey('users.User', related_name='tasks_assigned', on_delete=models.CASCADE)
    approvers = models.ManyToManyField('users.User', related_name='tasks_for_approval', through='Approval')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default=STATUS_NEW, choices=STATUS_CHOICES)


class Approval(models.Model):
    approver = models.ForeignKey(
        'users.User', related_name='approvals', on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        'tasks.Task', related_name='approvals', on_delete=models.CASCADE
    )
    is_approved = models.BooleanField(default=False)
