"""Composition class-module"""
from pathlib import Path
from typing import Union


class Composition:
    """Composition class"""
    def __init__(self, name: str, path: Union[str, Path], duration: float) -> None:
        """Initialization class"""
        self._name = str(name)
        self._path = Path(path)
        self._duration = float(duration)

    @property
    def name(self) -> str:
        """Return name of composition"""
        return self._name

    @property
    def path(self) -> Path:
        """Return path of composition"""
        return self._path

    @property
    def duration(self) -> float:
        """Return duration of composition"""
        return self._duration

    def __eq__(self, value: object) -> bool:
        """Set equal condition"""
        if not isinstance(value, Composition):
            return NotImplemented
        return self._name == value._name and self._path == value._path

    def __hash__(self) -> int:
        """allows you to use in hash-tables (set, array ...)"""
        return hash((self._name, self._path))

    def __str__(self) -> str:
        """return readeble format of class"""
        return f"(name: {self.name}, path: {self.path}, duration: {self.duration})"
