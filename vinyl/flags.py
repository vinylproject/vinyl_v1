import inspect


async def hi_there():
    pass


def is_async():
    return inspect.iscoroutinefunction(hi_there)

