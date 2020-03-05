from src.apps.tasks.models import Task


def test_task(db, task_factory, user_factory):
    # Статус новый, когда тикет только создан.
    task = task_factory()
    assert task.status == Task.STATUS_NEW

    # Если у тикета есть согласующие лица, то переходит в статус - Ждет согласования
    approver = user_factory()
    task.approvers.add(approver)
    assert task.status == Task.STATUS_PENDING

    more_approvers = user_factory.create_batch(3)
    for user in more_approvers:
        task.approvers.add(user)

    # После одного согласования, список ожидаемых лиц должен содержать всех, кроме согласовавшего
    task.approve(approver)
    assert set(task.pending_approvers()) == set(more_approvers)

    # После, как тикет согласован, назначенное лицо на исполнение тикета, 
    # переводит в статус “выполняется”. Был согласован полностью -> выполняется.
    for approver in task.approvers.all():
        task.approve(approver)
    assert task.status == Task.STATUS_INPROGRESS

    # После того, как назначенное лицо считает, что тикет выполнен, переводит тикет в статус - выполнено
    task.complete(task.assignee)
    assert task.status == Task.STATUS_COMPLETED

    # Автор тикета, проверяет работу и отправляет “на доработку”`
    task.request_changes(task.author)
    assert task.status == Task.STATUS_CHANGES_REQUESTED

    # Назначенное лицо снова выполняет тикет
    task.complete(task.assignee)
    assert task.status == Task.STATUS_COMPLETED

    # В конце, задачу может закрыть суперпользователь только
    superuser = user_factory(is_superuser=True)
    task.close(superuser)
    assert task.status == Task.STATUS_CLOSED
