"""
Module that contain playlist class
"""
from __future__ import annotations
from modules.composition import Composition
from modules.linkedlist import LinkedList, LinkedListItem


class PlayList(LinkedList):
    """playlist class"""
    def __init__(self, compositions: Composition = None):
        super().__init__(compositions)
        self._current_item: Composition | None = None

    @property
    def current(self) -> Composition | None:
        """
        Return current composition
        """
        if self._current_item is None:
            return None

        return self._current_item.data

    def play_all(self, item: Composition) -> Composition:
        """
        Return current composition, or set composition as first when current = None
        """
        if isinstance(item, Composition):
            item = self._find_item(item)

        elif not isinstance(item, LinkedListItem):
            raise TypeError("item must be Composition or LinkedListItem")

        self._current_item = item
        return self.current

    def find_composition_by_name(self, name: str) -> Composition | None:
        """
        Take name of composition and return object
        """
        for composition in self:
            if composition.data.name == name:
                return composition.data

        return None

    def _track_manager(self, pointer: str, border_getter: callable) -> Composition:
        """
        Class function that use in funcs: next_track, previous_track
        and return next track and previous track regarding current track
        """
        if self._current_item is None:
            self._current_item = self._first_item
            return self.current

        item = getattr(self._current_item, pointer)
        if item is None:
            item = border_getter()

        self._current_item = item
        return self.current

    def next_track(self) -> Composition:
        """
        Return next track
        """
        return self._track_manager("next_item", lambda: self.first_item)

    def previous_track(self) -> Composition:
        """
        Return previous_track
        """
        return self._track_manager("previous_item", self._get_last_item)
