from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = 'src.apps.tasks'

    def ready(self):
        import src.apps.tasks.signals
