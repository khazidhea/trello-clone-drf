import pytest

from django.core.exceptions import PermissionDenied

from src.apps.tasks.models import Task


def test_task_new_ok(db, task_factory):
    # Статус новый, когда тикет только создан.
    task = task_factory()
    assert task.status == Task.STATUS_NEW


def test_task_pending_ok(db, task_factory):
    # Если у тикета есть согласующие лица, то переходит в статус - Ждет согласования
    task = task_factory.pending()
    assert task.status == Task.STATUS_PENDING


def test_task_pending_approvers_ok(db, task_factory, user_factory):
    # После одного согласования, список ожидаемых лиц должен содержать всех, кроме согласовавшего
    task = task_factory()
    approvers = user_factory.create_batch(3)
    for user in approvers:
        task.approvers.add(user)
    assert len(task.pending_approvers()) == 3
    task.approve(approvers[0])
    assert len(task.pending_approvers()) == 2


def test_task_inprogress_ok(db, task_factory):
    # После, как тикет согласован, назначенное лицо на исполнение тикета, 
    # переводит в статус “выполняется”. Был согласован полностью -> выполняется.
    task = task_factory.inprogress()
    assert task.status == Task.STATUS_INPROGRESS


def test_task_completed_ok(db, task_factory):
    # После того, как назначенное лицо считает, что тикет выполнен, переводит тикет в статус - выполнено
    task = task_factory.completed()
    assert task.status == Task.STATUS_COMPLETED


def test_task_changes_requested_ok(db, task_factory):
    # Автор тикета, проверяет работу и отправляет “на доработку”
    task = task_factory.changes_requested()
    assert task.status == Task.STATUS_CHANGES_REQUESTED


def test_task_changes_requested_complete_again_ok(db, task_factory):
    # Назначенное лицо снова выполняет тикет
    task = task_factory.changes_requested()
    task.complete(task.assignee)
    assert task.status == Task.STATUS_COMPLETED


def test_task_closed_ok(db, task_factory, user_factory):
    # В конце, задачу может закрыть суперпользователь только
    task = task_factory.completed()
    superuser = user_factory(is_superuser=True)
    task.close(superuser)
    assert task.status == Task.STATUS_CLOSED


def test_task_approval_not_by_approver_permision_denied(db, task_factory, user_factory):
    task = task_factory.pending()
    user = user_factory()
    with pytest.raises(PermissionDenied):
        task.approve(user)


def test_task_completion_not_by_assignee_permision_denied(db, task_factory, user_factory):
    task = task_factory.inprogress()
    user = user_factory()
    with pytest.raises(PermissionDenied):
        task.complete(user)


def test_task_changes_requested_by_not_author_permission_denied(db, task_factory, user_factory):
    task = task_factory.completed()
    user = user_factory()
    with pytest.raises(PermissionDenied):
        task.request_changes(user)


def test_task_close_not_by_superuser_permision_denied(db, task_factory, user_factory):
    task = task_factory.completed()
    user = user_factory()
    with pytest.raises(PermissionDenied):
        task.close(user)
