import functools


def replace_chars(text, source, target):
    assert len(source) == len(target), f"Length mismatch between {source} and {target}"
    return "".join([dict(zip(source, target)).get(char, char) for char in text])


def skip_none(fun):
    @functools.wraps(fun)
    def wrapped(*args, **kwargs):
        if args[1] is None:
            return None
        return fun(*args, **kwargs)

    return wrapped
