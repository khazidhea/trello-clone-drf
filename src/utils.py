from functools import wraps

from django.core.exceptions import PermissionDenied


def permission_required(check):
    """
    Permission check based on the object and user_id

    Passes the object and user_id to the check function,
    calls for the decorated function if the check function to returns True,
    otherwise raises PermissionDenied exception
    """
    def decorator(fn):
        @wraps(fn)
        def permission_wrapper(instance, *args, **kwargs):
            user_id = args[0]
            if check(instance.task, user_id):
                return fn(instance, *args, **kwargs)
            else:
                raise PermissionDenied
        return permission_wrapper
    return decorator


def transition(source, dest, conditions=[]):
    """
    Adds transition to the machine named after decorated function

    Replaces the decorated function with the machine transition and calls it right after
    """
    def inner_transition(fn):
        @wraps(fn)
        def wrapper(instance, *args, **kwargs):
            if fn.__name__ not in instance.machine.events:
                # HACK: monkey patching pytransitions
                instance.machine._checked_assignment = lambda model, name, func: setattr(model, name, func)
                instance.machine.add_transition(
                    trigger=fn.__name__,
                    source=source,
                    dest=dest,
                    conditions=conditions
                )
            getattr(instance, fn.__name__)()
        return wrapper
    return inner_transition
