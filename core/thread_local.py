import threading

_thread_local = threading.local()


def set_current_business(business):
    _thread_local.current_business = business


def set_current_is_superuser(flag):
    _thread_local.is_superuser = flag


def get_current_business():
    return getattr(_thread_local, "current_business", None)


def get_current_user_is_superuser():
    return getattr(_thread_local, "is_superuser", False)
