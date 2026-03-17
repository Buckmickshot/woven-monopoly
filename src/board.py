import json
from dataclasses import dataclass
from typing import Any, Dict, List
from src.property import Property
from src.tiles import GoTile, Tile

@dataclass(frozen=True)
class Board:
    """Immutable representation of the game board."""
    tiles: List[Tile]

    def __post_init__(self) -> None:
        if not self.tiles:
            raise ValueError("Board must contain at least one space.")

    def __len__(self) -> int:
        return len(self.tiles)

    def space_at(self, index: int) -> Tile:
        """Returns the tile at a given index, wrapping around the board."""
        return self.tiles[index % len(self.tiles)]

    def property_indexes_by_colour(self) -> Dict[str, List[int]]:
        """Groups property indexes by colour."""
        result: Dict[str, List[int]] = {}

        for index, space in enumerate(self.tiles):
            if not isinstance(space, Property):
                continue

            result.setdefault(space.colour, []).append(index)

        return result
    
def _require_space_field(raw_space: Dict[str, Any], field_name: str, index: int) -> Any:
    """Ensures a required field exists in the raw JSON space."""

    if field_name not in raw_space:
        raise ValueError(f"Space at index {index} is missing required field '{field_name}'.")
    return raw_space[field_name]
    
def _validate_space(raw_space: Dict[str, Any], index: int) -> Tile:
    """Validates and converts a raw JSON space into a Tile object."""

    if not isinstance(raw_space, dict):
        raise ValueError(f"Space at index {index} must be an object.")

    name = _require_space_field(raw_space, "name", index)
    space_type = _require_space_field(raw_space, "type", index)

    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"Space at index {index} has invalid 'name'.")
    if not isinstance(space_type, str) or not space_type.strip():
        raise ValueError(f"Space at index {index} has invalid 'type'.")

    if space_type == "property":
        price = _require_space_field(raw_space, "price", index)
        colour = _require_space_field(raw_space, "colour", index)
        if not isinstance(price, int) or price <= 0:
            raise ValueError(f"Property '{name}' must have a positive integer price.")
        if not isinstance(colour, str) or not colour.strip():
            raise ValueError(f"Property '{name}' must have a non-empty colour.")

        return Property(name=name, price=price, colour=colour)

    elif space_type == "go":
        return GoTile(name=name)

    else:
        return Tile(name=name)

def load_board(board_path: str) -> Board:
    """Loads and validates a board configuration from JSON."""

    with open(board_path) as f:
        raw_content = json.load(f)

    if not isinstance(raw_content, list):
        raise ValueError("Board JSON must be an array of tiles.")

    tiles = [
        _validate_space(raw_space, index)
        for index, raw_space in enumerate(raw_content)
    ]

    if not tiles:
        raise ValueError("Board must not be empty.")

    if not isinstance(tiles[0], GoTile):
        raise ValueError("First board space must be GO.")

    return Board(tiles=tiles)