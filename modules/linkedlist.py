"""
Module that contains class LinkedList
with class items of linkedlist - LinkedListItem
"""
from __future__ import annotations
from collections.abc import Iterator


class LinkedListItem:
    """Class of linked list items"""
    def __init__(self, data: object) -> None:
        """initialization class"""
        self.data: object = data
        self._prev: LinkedListItem | None = None
        self._next: LinkedListItem | None = None

    @property
    def next_item(self) -> LinkedListItem | None:
        """get next item"""
        return self._next

    @next_item.setter
    def next_item(self, data: LinkedListItem | None) -> None:
        """set next item"""
        if data is not None and not isinstance(data, LinkedListItem):
            raise TypeError("next_item must be LinkedListItem or None")

        self._next = data

        if data is not None and data.previous_item is not self:
            data.previous_item = self

    @property
    def previous_item(self) -> LinkedListItem | None:
        """get previous item"""
        return self._prev

    @previous_item.setter
    def previous_item(self, data: LinkedListItem | None) -> None:
        """set previous item"""
        if data is not None and not isinstance(data, LinkedListItem):
            raise TypeError("previous_item must be LinkedListItem or None")

        self._prev = data

        if data is not None and data.next_item is not self:
            data.next_item = self

class LinkedList:
    """
    Class of linkedlist, which implements the
    capabilities of a doubly linked circular list
    """
    def __init__(self, first_item: LinkedListItem | None = None) -> None:
        """Initialization class"""
        self._first_item: LinkedListItem | None = first_item
        self._size: str = 0
        self._next_cursor: LinkedListItem | None = None

        if first_item is not None:
            item = first_item
            while True:
                self._size += 1
                item = item.next_item
                if item is first_item:
                    break

    def append_right(self, data: object | list | tuple) -> LinkedListItem | None:
        """Func append element in at the end of the list"""
        if data is None:
            return None

        if not isinstance(data, (list, tuple)):
            data = (data,)

        item = None
        for it in data:
            item = LinkedListItem(it)

            if self._first_item is None:
                item.next_item = item
                item.previous_item = item
                self._first_item = item
            else:
                first = self._first_item
                last = first.previous_item

                item.next_item = first
                item.previous_item = last
                last.next_item = item
                first.previous_item = item

            self._size += 1

        return item

    def append(self, data: object | list | tuple) -> LinkedListItem | None:
        """Alias of append_right"""
        return self.append_right(data)

    def append_left(self, data: object | list | tuple) -> LinkedListItem | None:
        """Func append element in at the start of the list"""
        if data is None:
            return None

        if not isinstance(data, (list, tuple)):
            data = (data,)

        item = None
        for it in reversed(data):
            item = LinkedListItem(it)

            if self._first_item is None:
                item.next_item = item
                item.previous_item = item
                self._first_item = item
            else:
                first = self._first_item
                last = first.previous_item

                item.next_item = first
                item.previous_item = last
                self._first_item = item

            self._size += 1

        return item

    @property
    def first_item(self) -> LinkedListItem | None:
        """get first item of linkedlist"""
        return self._first_item

    @first_item.setter
    def first_item(self, data: LinkedListItem | None) -> None:
        """set first item of linkedlist"""
        self._first_item = data

    def _get_last_item(self) -> LinkedListItem | None:
        """get last item of linkedlist"""
        if self._size == 0:
            return None

        item = self.first_item
        while item.next_item is not None:
            item = item.next_item

        return item

    @property
    def last(self) -> LinkedListItem | None:
        """
        public method that return last element of
        linkedlist with check on None
        """
        if self._first_item is None:
            return None

        return self._first_item.previous_item

    def _find_item(self, data: object) -> LinkedListItem:
        """
        data(str, int or any type of items in linkedlist) -> linkedlistitem"""
        if self._first_item is None:
            raise ValueError(f"{data!r} isn't in linkedlist")

        item = self._first_item

        while True:
            if item.data == data:
                return item

            item = item.next_item
            if item is self._first_item:
                raise ValueError(f"{data!r} isn't in linkedlist")

    def _remove_link(self, item: LinkedListItem) -> None:
        """func that remove links of deleting item or relocatable item"""
        if self._size == 1:
            item.next_item = None
            item.previous_item = None
            self._first_item = None
            self._size = 0
            return

        item_prev = item.previous_item
        item_next = item.next_item

        if item_prev is None:
            self._first_item = item_next
        else:
            item_prev.next_item = item_next

        if item_next is not None:
            item_next.previous_item = item_prev

        item.previous_item = None
        item.next_item = None
        self._size -= 1

    def remove(self, data: object) -> None:
        """func that remove item and relocate links"""
        item = self._find_item(data)
        return self._remove_link(item)

    def insert(self, previous: object | LinkedListItem, data: object) -> LinkedListItem:
        """func that adding item after current item"""
        if isinstance(previous, LinkedListItem):
            prev = previous
        else:
            prev = self._find_item(previous)

        item = LinkedListItem(data)
        prev_next = prev.next_item

        if prev_next is not None:
            prev_next.previous_item = item
            item.next_item = prev_next

        prev.next_item = item
        item.previous_item = prev
        self._size += 1

        return item

    def __len__(self) -> int:
        """magical func that can return len of linkedlist"""
        return self._size

    def __iter__(self) -> Iterator[LinkedListItem]:
        """magical func that can make iteration on linkedlist"""
        if self._first_item is None:
            return

        item = self._first_item

        while True:
            yield item
            item = item.next_item
            if item is self._first_item:
                break

    def __getitem__(self, key: int) -> object:
        """magical func that can return item by key"""
        if key < 0:
            key = self._size + key

        if not 0 <= key < self._size:
            raise IndexError("Index is out of range")

        item = self._first_item
        for _ in range(key):
            item = item.next_item

        return item.data

    def __contains__(self, data: object) -> bool:
        """magical func that supports operator 'in'"""
        if self._first_item is None:
            return False

        item = self._first_item
        while True:
            if item.data == data:
                return True
            item = item.next_item
            if item is self._first_item:
                return False

    def __reversed__(self) -> Iterator[object]:
        """reverse linkedlist for iteration"""
        if self._first_item is None:
            return

        item = self.last

        while True:
            yield item.data
            if item is self._first_item:
                break

            item = item.previous_item

    def __next__(self) -> object:
        """get next data, create iterator"""
        if self._next_cursor is None:
            self._next_cursor = self._first_item
            raise StopIteration

        data = self._next_cursor.data
        self._next_cursor = self._next_cursor.next_item

        return data

    def _return_str(self) -> str:
        """
        auxiliary function than uses in magical methods __str__ and __repr__
        """
        string = ""

        for el in self:
            string += "<- " + str(el) + " -> "
        
        return string

    def __str__(self) -> str:
        """
        return text interpretation of linked list like:
        <- element_1 -> <- element_2 -> ... -> <- element_n ->
        """
        return self._return_str()

    def __repr__(self) -> str:
        """
        return text interpretation of linked list like:
        <- element_1 -> <- element_2 -> ... -> <- element_n ->
        support nested structure
        """

        return self._return_str()
