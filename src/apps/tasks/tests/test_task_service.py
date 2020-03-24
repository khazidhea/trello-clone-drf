import pytest

from django.core.exceptions import PermissionDenied

from src.apps.tasks.models import Task, Approval
from src.apps.tasks.services import TaskService


def test_task_service_to_pending_ok(db, task_factory):
    task = task_factory()
    service = TaskService(task)
    service.to_pending()
    assert task.status == Task.STATUS_PENDING


def test_task_service_to_inprogress_ok(db, task_factory):
    task = task_factory.pending()
    approval = Approval.objects.get(task=task)
    approval.is_approved = True
    approval.save()
    TaskService(task).to_inprogress()
    assert task.status == Task.STATUS_INPROGRESS


def test_task_service_to_inprogress_not_approved(db, task_factory):
    task = task_factory.pending()
    TaskService(task).to_inprogress()
    assert task.status == Task.STATUS_PENDING


def test_task_service_complete_ok(db, task_factory):
    task = task_factory.inprogress()
    TaskService(task).complete(task.assignee.id)
    assert task.status == Task.STATUS_COMPLETED


def test_task_service_complete_not_by_assignee(db, task_factory, user_factory):
    task = task_factory.inprogress()
    user = user_factory()
    with pytest.raises(PermissionDenied):
        TaskService(task).complete(user.id)


def test_task_service_request_changes_ok(db, task_factory):
    task = task_factory.completed()
    TaskService(task).request_changes(task.author.id)
    assert task.status == Task.STATUS_CHANGES_REQUESTED


def test_task_service_request_changes_not_by_author(db, task_factory, user_factory):
    task = task_factory.completed()
    user = user_factory()
    with pytest.raises(PermissionDenied):
        TaskService(task).request_changes(user.id)


def test_task_service_changes_requested_complete_again_ok(db, task_factory):
    task = task_factory.changes_requested()
    TaskService(task).complete(task.assignee.id)
    assert task.status == Task.STATUS_COMPLETED


def test_task_service_closed_ok(db, task_factory, user_factory):
    task = task_factory.completed()
    superuser = user_factory(is_superuser=True)
    TaskService(task).close(superuser.id)
    assert task.status == Task.STATUS_CLOSED


def test_task_service_closed_ok_not_by_superuser(db, task_factory, user_factory):
    task = task_factory.completed()
    user = user_factory()
    with pytest.raises(PermissionDenied):
        TaskService(task).close(user.id)


def test_task_service_add_approver_ok(db, task_factory, user_factory):
    approver = user_factory()
    task = task_factory()
    TaskService(task).add_approver(approver)
    assert task.status == Task.STATUS_PENDING
    assert approver in task.approvers.all()
