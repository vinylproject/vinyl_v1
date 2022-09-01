import threading
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar

from django.db import connections

from vinyl import patches

# TODO rename?
statements = ContextVar('statements')


class StatementsList(list):
    using = None


@asynccontextmanager
async def execute_statements():
    token = statements.set(value := StatementsList())
    try:
        yield value
        if not value:
            return
        connection = connections[value.using]
        async with connection.transaction():
            for sql, params in value:
                await connection.execute_only(sql, params)
    finally:
        statements.reset(token)

tl = threading.local()
tl.collected_sql = None

@contextmanager
def collect_sql():
    tl.collected_sql = value = StatementsList()
    try:
        yield value
    finally:
        tl.collected_sql = ()

# is collecting sql
# get collected sql


class DeferredMixin:

    @asynccontextmanager
    async def _deferred(self):
        async with execute_statements():
            cls = self.__class__
            self.__class__ = self._deferred_model
            try:
                with patches.apply():
                    yield
            finally:
                self.__class__ = cls
