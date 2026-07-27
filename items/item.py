from dataclasses import dataclass
from typing import ClassVar


@dataclass(kw_only=True)
class Item:
    item_code: str = ""
    max_stack: ClassVar[int] = 1
