from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from src.board import Board
from src.player import Player

@dataclass(frozen=True)
class GameConfig:
    """
    Configuration for a game simulation.

    Attributes:
        player_names: Names of players in turn order.
        starting_money: Initial cash assigned to each player.
        pass_go_reward: Amount awarded when passing GO.
        stop_on_bankruptcy: Whether the game stops when any player goes bankrupt.
    """
    player_names: List[str]
    starting_money: int = 16
    pass_go_reward: int = 1
    stop_on_bankruptcy: bool = True
    
@dataclass(frozen=True)
class GameResult:
    """
    Result of a game simulation.

    Attributes:
        ranking: List of (cash, player_names) tuples, sorted by cash in descending order.
        cash_by_player: Mapping of player names to their final cash amounts.
        position_by_player: Mapping of player names to their final positions.
        turns_played: Number of turns played.
        turn_log: Optional list of strings describing events during the game.
    """
    ranking: List[Tuple[int, List[str]]]
    cash_by_player: Dict[str, int]
    position_by_player: Dict[str, str]
    turns_played: int
    turn_log: Optional[List[str]] = None

class Game:
    """
    Deterministic game engine for a fixed board and roll sequence.

    The game is fully deterministic given:
    - initial configuration
    - board layout
    - sequence of dice rolls
    """

    def __init__(self, board: Board, config: GameConfig):
        if not config.player_names:
            raise ValueError("At least one player is required.")
        if config.starting_money < 0:
            raise ValueError("Starting money cannot be negative.")
        if config.pass_go_reward < 0:
            raise ValueError("Pass GO reward cannot be negative.")

        self.board = board
        self.config = config
        self.players = [Player(name=name, cash=config.starting_money) for name in config.player_names]
        self.property_indexes_by_colour = board.property_indexes_by_colour()

    def play(self, rolls: List[int], include_turn_log: bool = False) -> GameResult:
        """
        Simulates the game using a fixed sequence of dice rolls.

        Args:
            rolls: List of positive integers representing dice rolls.
            include_turn_log: Whether to record per-turn events.

        Returns:
            GameResult containing final state and optional log.

        Notes:
            - Game proceeds in round-robin player order.
            - Simulation stops early if stop_on_bankruptcy is True and any player is bankrupt.
        """

        turn_log: List[str] = []

        if not rolls:
            raise ValueError("Rolls must not be empty.")

        if any((not isinstance(roll, int) or roll <= 0) for roll in rolls):
            raise ValueError("Rolls must be positive integers.")

        turn_index = 0
        while turn_index < len(rolls):
            current_player = self.players[turn_index % len(self.players)]
            roll = rolls[turn_index]
            start_position = current_player.position
            start_tile = self.board.space_at(start_position)

            passed_go = current_player.move(steps=roll, board_size=len(self.board))
            landed_index = current_player.position
            landed_tile = self.board.space_at(landed_index)

            if include_turn_log:
                turn_log.append(
                    f"Turn {turn_index + 1}: {current_player.name} moved {roll} spaces from {start_tile.name}."
                )

            if passed_go:
                current_player.credit(self.config.pass_go_reward)
                if include_turn_log:
                    turn_log.append(
                        f"      {current_player.name} passed GO, receiving ${self.config.pass_go_reward}."
                    )

            landing_tile_msg = landed_tile.land(current_player, self)
            if landing_tile_msg and include_turn_log:
                turn_log.append(landing_tile_msg)

            if self.config.stop_on_bankruptcy and any(player.is_bankrupt for player in self.players):
                break

            turn_index += 1

        groups = defaultdict(list)

        for p in self.players:
            groups[p.cash].append(p.name)

        # Group players by cash and sort deterministically.
        # Names within each group are sorted to ensure stable output for testing.
        ranking = []
        for cash, names in groups.items():
            ranking.append((cash, sorted(names)))

        ranking.sort(reverse=True)

        turns_played = turn_index + 1
        cash_by_player = {player.name: player.cash for player in self.players}
        position_by_player = {
            player.name: self.board.space_at(player.position).name for player in self.players
        }

        return GameResult(
            ranking=ranking,
            cash_by_player=cash_by_player,
            position_by_player=position_by_player,
            turns_played=turns_played,
            turn_log=turn_log if include_turn_log else None,
        )
    
    def owns_full_colour_set(self, owner: Player, colour: str) -> bool:
        """
        Checks whether a player owns all properties of a given colour.

        Args:
            owner: The player to check.
            colour: The property colour group.

        Returns:
            True if the player owns all properties of that colour, False otherwise.
        """
        colour_indexes = self.property_indexes_by_colour.get(colour, [])
        return bool(colour_indexes) and all(
            index in owner.owned_property_indexes
            for index in colour_indexes
        )