# Copyright 2015, Kai Groner <kai@gronr.com>
# Release under the simplified BSD license.  See LICENSE for details.

import asyncio
import functools


__all__ = []
def export(f):
    __all__.append(f.__name__)
    return f


class AsyncChannel:
    '''A channel supporting asynchronous iteration.'''

    def __init__(self):
        self._putting = None
        self._getting = None
        self._ended = asyncio.Future()

    async def put(self, item):
        '''Put an item on the channel.

        Concurrent put operations are an error.
        '''

        if self._putting is not None:
            raise RuntimeError('Channel put() already in progress')

        if self._ended.done():
            raise ValueError('Cannot put() to a closed channel')

        if self._getting is not None:
            # There is already a get pending, we can just hand the value off.
            getting, self._getting = self._getting, None
            getting.set_result(item)
            return # synchronously -- fast

        putted = asyncio.Future()
        self._putting = item, putted
        await putted

    async def __aiter__(self):
        return self

    async def __anext__(self):
        '''Get an item from the channel.

        Concurrent reads from the channel are an error.
        '''

        if self._getting is not None:
            raise RuntimeError('Channel get() already in progress')

        if self._putting is not None:
            # There is already a put pending, we're nearly done!
            (item, putted), self._putting = self._putting, None
            putted.set_result(None)
            return item # synchronously -- fast

        if self._ended.done():
            raise StopAsyncIteration(await self._ended)

        # Instead of using the complicated (and maybe slower) asyncio.wait()
        # API, we'll just make close/abort resolve any pending get operation
        # directly.
        self._getting = asyncio.Future()
        return await self._getting

    async def close(self):
        '''Close the channel.

        If the channel contains an unread item, close waits for it to be read
        before completing.
        '''

        self._ended.set_result(None)
        if self._getting:
            getting, self._getting = self._getting, None
            getting.set_exception(StopAsyncIteration())
        elif self._putting is not None:
            await self._putting[1]

    async def abort(self, err):
        '''Close the channel with an error.

        The error will be propagated to any consumer of the channel.

        If the channel contains an unread item, abort waits for it to be read
        before completing.  Is this desirable?
        '''

        self._ended.set_exception(err)
        if self._getting:
            getting, self._getting = self._getting, None
            getting.set_exception(err)
        elif self._putting is not None:
            await self._putting[1]


@export
def alternator(fn):
    '''Adapt a coroutine to work like a generator.

    The wrapped function will return an AsyncChannel instance.  It should
    accept as it's first argument, a yeeld function.  Calling the yeeld
    function, and awaiting the result writes to the channel.  When the function
    ends the channel will be closed (or aborted if an exception is raised.)
    '''

    async def task(channel, a, kw):
        try:
            await fn(channel.put, *a, **kw)
        except BaseException as e:
            # Exceptions should propagate to the channel
            await channel.abort(e)
        else:
            await channel.close()

    @functools.wraps(fn)
    def wrapper(*a, **kw):
        channel = AsyncChannel()
        asyncio.ensure_future(task(channel, a, kw))
        return channel

    return wrapper
