from django.db.models.signals import m2m_changed

from src.apps.tasks.models import Task


def approvers_changed(sender, instance, action, **kwargs):
    if instance.status == Task.STATUS_NEW:
        if action == 'post_add':
            instance.to_status_pending()


m2m_changed.connect(approvers_changed, sender=Task.approvers.through)
