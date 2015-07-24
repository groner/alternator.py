# Copyright 2015, Kai Groner <kai@gronr.com>
# Release under the simplified BSD license.  See LICENSE for details.

from .generator import alternator


__all__ = []
def export(f):
    __all__.append(f.__name__)
    return f


Unspecified = object()


@export
@alternator
async def acollect(yeeld, fn, aseq):
    async for item in aseq:
        await fn(yeeld, item)

@export
@alternator
async def amap(yeeld, fn, aseq):
    async for item in aseq:
        await yeeld(await fn(item))

@export
@alternator
async def afilter(yeeld, fn, aseq):
    async for item in aseq:
        if await fn(item):
            await yeeld(item)
        await yeeld(await fn(item))

@export
async def areduce(fn, aseq, initial=Unspecified):
    ai = aiter(aseq)
    if initial is Unspecified:
        acc = await anext(ai, Unspecified)
    else:
        acc = initial
    if acc is Unspecified:
        raise TypeError('areduce() of empty sequence with no initial value')
    async for item in ai:
        if acc is Unspecified:
            acc = item
        else:
            acc = await fn(acc, item)
    return acc
