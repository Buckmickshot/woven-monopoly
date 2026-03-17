import json
from dataclasses import dataclass
from typing import Any, Dict, List
from property import Property
from tiles import GoTile, Tile

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
    
def _require_space_field(raw_space: Dict[str, Any], field_name: str, index: int) -> Any:
    if field_name not in raw_space:
        raise ValueError(f"Space at index {index} is missing required field '{field_name}'.")
    return raw_space[field_name]
    
def _validate_space(raw_space: Dict[str, Any], index: int) -> Tile:
    if not isinstance(raw_space, dict):
        raise ValueError(f"Space at index {index} must be an object.")

    name = _require_space_field(raw_space, "name", index)
    space_type = _require_space_field(raw_space, "type", index)

    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"Space at index {index} has invalid 'name'.")

    if space_type == "property":
        price = _require_space_field(raw_space, "price", index)
        colour = _require_space_field(raw_space, "colour", index)

        return Property(name=name, price=price, colour=colour)

    elif space_type == "go":
        return GoTile(name=name)

    else:
        return Tile(name=name)

def load_board(board_path: str) -> Board:
    with open(board_path) as f:
        raw_content = json.load(f)

    if not isinstance(raw_content, list):
        raise ValueError("Board JSON must be an array of spaces.")

    spaces = [
        _validate_space(raw_space, index)
        for index, raw_space in enumerate(raw_content)
    ]

    if not spaces:
        raise ValueError("Board must not be empty.")

    if not isinstance(spaces[0], GoTile):
        raise ValueError("First board space must be GO.")

    return Board(spaces)