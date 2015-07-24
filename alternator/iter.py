# Copyright 2015, Kai Groner <kai@gronr.com>
# Release under the simplified BSD license.  See LICENSE for details.

__all__ = []
def export(f):
    __all__.append(f.__name__)
    return f


Unspecified = object()


@export
def aiter(x):
    '''aiter(iterable)'''
    return x.__aiter__()

@export
def anext(ai, default=Unspecified):
    '''anext(iterator[, default])'''
    if default is Unspecified:
        return ai.__anext__()
    return _anext_with_default(ai, default)

async def _anext_with_default(ai, default):
    try:
        return await ai.__anext__()
    except StopAsyncIteration:
        return default
