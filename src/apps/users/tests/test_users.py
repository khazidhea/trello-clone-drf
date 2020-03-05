def test_user(db, user_factory):
    user = user_factory()
    assert user
