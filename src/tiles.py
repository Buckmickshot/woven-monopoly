from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from game import Game


@dataclass
class Tile(ABC):
    """Base class for all board tiles."""

    name: str

    @abstractmethod
    def land(self, player: Player, game: Game) -> None:
        """Called when a player lands on this tile."""
        pass


@dataclass
class GoTile(Tile):
    """Represents the GO tile."""

    def land(self, player: Player, game: Game) -> None:
        pass