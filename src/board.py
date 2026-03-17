import json
from dataclasses import dataclass
from typing import Dict, List
from property import Property
from tiles import Tile


def load_board(board_path):
    with open(board_path) as f:
        return json.load(f)
    
@dataclass(frozen=True)
class Board:
    spaces: List[Tile]

    def __post_init__(self) -> None:
        if not self.spaces:
            raise ValueError("Board must contain at least one space.")

    def __len__(self) -> int:
        return len(self.spaces)

    def space_at(self, index: int) -> Tile:
        return self.spaces[index % len(self.spaces)]

    def property_indexes_by_colour(self) -> Dict[str, List[int]]:
        result: Dict[str, List[int]] = {}

        for index, space in enumerate(self.spaces):
            if not isinstance(space, Property):
                continue

            result.setdefault(space.colour, []).append(index)

        return result