import asyncio
import unittest

from alternator import alternator, aiter, anext
from alternator.generator import AsyncChannel

from tests.asynchelpers import AsyncTestBase, run_until_complete, achain
from tests.asynchelpers import momentarily


class TestAsyncChannel(AsyncTestBase, unittest.TestCase):
    @run_until_complete
    async def test_put_before_get(self):
        channel = AsyncChannel()
        put, get = await asyncio.gather(
                channel.put('foo'),
                momentarily(1, anext(channel)))
        self.assertIsNone(put)
        self.assertEqual(get, 'foo')

    @run_until_complete
    async def test_get_before_put(self):
        channel = AsyncChannel()
        get, put = await asyncio.gather(
                anext(channel),
                momentarily(1, channel.put('foo')))
        self.assertIsNone(put)
        self.assertEqual(get, 'foo')

    @run_until_complete
    async def test_double_put_error(self):
        channel = AsyncChannel()
        with self.assertRaises(RuntimeError):
            put, put = await asyncio.gather(
                    channel.put('foo'),
                    momentarily(1, channel.put('bar')))

    @run_until_complete
    async def test_double_get_error(self):
        channel = AsyncChannel()
        with self.assertRaises(RuntimeError):
            put, put = await asyncio.gather(
                    channel.put('foo'),
                    momentarily(1, channel.put('bar')))

    @run_until_complete
    async def test_close(self):
        channel = AsyncChannel()
        await channel.close()
        with self.assertRaises(StopAsyncIteration):
            await anext(channel)
        with self.assertRaises(ValueError):
            await channel.put('foo')

    @run_until_complete
    async def test_close_with_pending_get(self):
        channel = AsyncChannel()
        with self.assertRaises(StopAsyncIteration):
            get, close = await asyncio.gather(
                    anext(channel),
                    momentarily(1, channel.close()))

        with self.assertRaises(StopAsyncIteration):
            await anext(channel)
        with self.assertRaises(ValueError):
            await channel.put('foo')

    @run_until_complete
    async def test_close_with_pending_put(self):
        channel = AsyncChannel()
        put, close, get = await asyncio.gather(
                channel.put('foo'),
                momentarily(1, channel.close()),
                momentarily(2, anext(channel)))
        self.assertIsNone(put)
        self.assertIsNone(close)
        self.assertEqual(get, 'foo')

        with self.assertRaises(StopAsyncIteration):
            await anext(channel)
        with self.assertRaises(ValueError):
            await channel.put('foo')

    @run_until_complete
    async def test_abort(self):
        channel = AsyncChannel()
        await channel.abort(MadeUpError())
        with self.assertRaises(MadeUpError):
            await anext(channel)
        with self.assertRaises(ValueError):
            await channel.put('foo')

    @run_until_complete
    async def test_abort_with_pending_get(self):
        channel = AsyncChannel()
        with self.assertRaises(MadeUpError):
            get, abort = await asyncio.gather(
                    anext(channel),
                    momentarily(1, channel.abort(MadeUpError())))

        with self.assertRaises(MadeUpError):
            await anext(channel)
        with self.assertRaises(ValueError):
            await channel.put('foo')

    @run_until_complete
    async def test_abort_with_pending_put(self):
        channel = AsyncChannel()
        put, abort, get = await asyncio.gather(
                channel.put('foo'),
                momentarily(1, channel.abort(MadeUpError())),
                momentarily(2, anext(channel)))
        self.assertIsNone(put)
        self.assertIsNone(abort)
        self.assertEqual(get, 'foo')

        with self.assertRaises(MadeUpError):
            await anext(channel)
        with self.assertRaises(ValueError):
            await channel.put('foo')

    @run_until_complete
    async def test_alternator(self):
        @alternator
        async def foo(yeeld, aseq):
            async for x in aseq:
                await yeeld(x+1)

        g = foo(achain(range(3)))

        self.assertEqual(await anext(g), 1)
        self.assertEqual(await anext(g), 2)
        self.assertEqual(await anext(g), 3)
        with self.assertRaises(StopAsyncIteration):
            await anext(g)


class MadeUpError(Exception):
    '''Guaranteed not to come from any source.'''


if __name__ == '__main__':
    unittest.main()
