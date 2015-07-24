import asyncio
import functools
import time
import unittest


__all__ = []
def export(f):
    __all__.append(f.__name__)
    return f


@export
def run_until_complete(fn):
    '''Decorator to run an async test synchronously.
    
    Use with AsyncTestBase.
    '''
    @functools.wraps(fn)
    def wrapper(self, *a, **kw):
        timeout = self.async_test_timeout

        self.loop.run_until_complete(
                asyncio.wait_for(fn(self, *a, **kw), timeout))
    return wrapper


@export
class AsyncTestBase:
    '''Async test base.

    Creates a new event loop for each test.
    '''

    async_test_timeout = 3

    def setUp(self):
        super().setUp()
        self.saved_loop = asyncio.get_event_loop()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.stop()
        self.loop.close()
        asyncio.set_event_loop(self.saved_loop)
        super().tearDown()


@export
class achain:
    '''Async generator from sequences.'''

    def __init__(self, *seqs):
        self.seqs = seqs

    async def __aiter__(self):
        return _achainiter(self)


class _achainiter:
    def __init__(self, achain):
        self.seqs = iter(achain.seqs)
        self.iter = iter(())

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            try:
                self.iter = iter(next(self.seqs))
            except StopIteration:
                raise StopAsyncIteration
            return await self.__anext__()


@export
@asyncio.coroutine
def momentarily(beats, coro):
    '''yield for a number of beats before yielding to a coroutine.'''
    for _ in range(beats):
        yield # let something else run
    return (yield from coro)


# No need to keep running this everytime.
@unittest.skip('because it worked')
class TestAsyncTestBase(AsyncTestBase, unittest.TestCase):
    @run_until_complete
    async def test_sleep(self):
        '''just a second'''
        t1 = time.monotonic()
        await asyncio.sleep(1)
        t2 = time.monotonic()
        self.assertAlmostEqual(t2-t1, 1, places=1)
