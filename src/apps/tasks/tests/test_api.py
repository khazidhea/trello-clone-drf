def test_task_new(db, client, user_factory):
    author = user_factory()
    assignee = user_factory()
    response = client.post(
        '/api/tasks/',
        {
            'title': 'test',
            'author': author.id,
            'assignee': assignee.id
        }
    )
    assert response.status_code == 201
    assert response.json()['id'] == 1


def test_task_add_approver(db, client, user_factory, task_factory):
    task = task_factory()
    approver = user_factory()
    response = client.post('/api/tasks/1/approvers/', {'id': approver.id})
    assert response.status_code == 201
    assert approver in task.approvers.all()


def test_task_list_approvers(db, client, task_factory):
    task = task_factory.inprogress()
    response = client.get('/api/tasks/1/approvers/')
    assert response.status_code == 200
    assert len(response.json()) == len(task.approvers.all())


def test_task_delete_approvers(db, client, user_factory, task_factory):
    task = task_factory.inprogress()
    approver = task.approvers.all()[0]
    len_before = len(task.approvers.all())
    response = client.delete('/api/tasks/1/approvers/{}/'.format(approver.id))
    assert response.status_code == 204
    assert len(task.approvers.all()) == len_before - 1