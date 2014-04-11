__author__ = 'whiord'

import json
import io


class Configuration(object):
    pass


def open_json(file_name):
    with io.open(file_name) as fd:
        js = json.load(fd)

    return construct(js)


def construct(js):
    if isinstance(js, list):
        res = [construct(val) for val in js]
        return res
    elif isinstance(js, dict):
        res = Configuration()
        for key, value in js.items():
            res.__setattr__(key, construct(value))
        return res
    else:
        return js
