# `ports.py` defines interfaces to be used (or be implemented) by outer layers

import abc


class WriteOnlyRepo(abc.ABC):
    def save(self, data, name, **kwargs):
        raise Exception("Not Implemented!")


class ReadOnlyRepo(abc.ABC):
    def get(self, key, **kwargs):
        raise Exception("Not Implemented!")
