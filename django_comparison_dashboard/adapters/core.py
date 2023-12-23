from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


class AdapterRegistry:
    _instance = None
    sources = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, source: type[DataAdapter]):
        cls.sources[source.name] = source

    def __getitem__(self, item):
        if item in self.sources:
            return self.sources[item]
        raise KeyError(
            f"Can not find adapter '{item}' in adapter registry. Maybe you forgot to register it in the first place?"
        )


class DataAdapter(abc.ABC):
    """Base class for data adapters"""

    name: str = None

    @classmethod
    @abc.abstractmethod
    def transform(cls, data: list[dict] | pd.DataFrame):
        raise NotImplementedError("Transform function must be implemented in child adapter class")
