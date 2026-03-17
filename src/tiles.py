from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.player import Player
    from src.game import Game


@dataclass
class Tile(ABC):
    """Base class for all board tiles."""

    name: str

    @abstractmethod
    def land(self, player: Player, game: Game) -> Optional[str]:
        """Called when a player lands on this tile."""
        pass


@dataclass
class GoTile(Tile):
    """Represents the GO tile."""

    def land(self, player: Player, game: Game) -> Optional[str]:
        return None