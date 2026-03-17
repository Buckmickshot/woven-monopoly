from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from tiles import Tile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from game import Game


@dataclass
class Property(Tile):
    """Represents a purchasable board property."""

    price: int
    colour: str
    owner: Optional[Player] = None

    @property
    def is_owned(self) -> bool:
        return self.owner is not None

    @property
    def base_rent(self) -> int:
        return self.price

    def land(self, player: Player, game: Game) -> None:
        """Handle logic when a player lands on this property."""

        # Case 1 — unowned → must buy
        if not self.is_owned:
            player.debit(self.price)
            self.owner = player
            player.owned_property_indexes.add(player.position)

        # Case 2 — owned by someone else → pay rent
        elif self.owner != player:
            owner = self.owner
            rent = self.base_rent

            if game.owns_full_colour_set(owner, self.colour):
                rent *= 2

            player.debit(rent)
            owner.credit(rent)

        # Case 3 — owned by self → do nothing