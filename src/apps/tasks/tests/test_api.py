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
