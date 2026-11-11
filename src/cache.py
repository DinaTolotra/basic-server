from typing import Optional

from src.model import Item


class ItemCache:
    def __init__(self) -> None:
        self._data: dict[int, Item] = {}

    def __getitem__(self, item_id: int) -> Optional[Item]:
        return self._data.get(item_id, None)

    def __setitem__(self, item_id: int, item: Item) -> None:
        self._data.update([(item_id, item)])

    def __delitem__(self, item_id: int) -> None:
        del self._data[item_id]
    
    def clear(self) -> None:
        self._data.clear()
