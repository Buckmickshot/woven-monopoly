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
            raise ValueError("Board must contain at least one tile.")

    def __len__(self) -> int:
        return len(self.tiles)

    def tile_at(self, index: int) -> Tile:
        """Returns the tile at a given index, wrapping around the board."""
        return self.tiles[index % len(self.tiles)]

    def property_indexes_by_colour(self) -> Dict[str, List[int]]:
        """Groups property indexes by colour."""
        result: Dict[str, List[int]] = {}

        for index, tile in enumerate(self.tiles):
            if not isinstance(tile, Property):
                continue

            result.setdefault(tile.colour, []).append(index)
        return result
    
def _require_tile_field(raw_tile: Dict[str, Any], field_name: str, index: int) -> Any:
    """Ensures a required field exists in the raw JSON tile."""

    if field_name not in raw_tile:
        raise ValueError(f"Tile at index {index} is missing required field '{field_name}'.")
    return raw_tile[field_name]
    
def _validate_tile(raw_tile: Dict[str, Any], index: int) -> Tile:
    """Validates and converts a raw JSON tile into a Tile object."""

    if not isinstance(raw_tile, dict):
        raise ValueError(f"Tile at index {index} must be an object.")

    name = _require_tile_field(raw_tile, "name", index)
    tile_type = _require_tile_field(raw_tile, "type", index)

    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"Tile at index {index} has invalid 'name'.")
    if not isinstance(tile_type, str) or not tile_type.strip():
        raise ValueError(f"Tile at index {index} has invalid 'type'.")

    if tile_type == "property":
        price = _require_tile_field(raw_tile, "price", index)
        colour = _require_tile_field(raw_tile, "colour", index)
        if not isinstance(price, int) or price <= 0:
            raise ValueError(f"Property '{name}' must have a positive integer price.")
        if not isinstance(colour, str) or not colour.strip():
            raise ValueError(f"Property '{name}' must have a non-empty colour.")

        return Property(name=name, price=price, colour=colour)

    elif tile_type == "go":
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
        _validate_tile(raw_tile, index)
        for index, raw_tile in enumerate(raw_content)
    ]

    if not tiles:
        raise ValueError("Board must not be empty.")

    if not isinstance(tiles[0], GoTile):
        raise ValueError("First board tile must be GO.")

    return Board(tiles=tiles)