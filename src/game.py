from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from board import Board
from player import Player

@dataclass(frozen=True)
class GameConfig:
    player_names: List[str]
    starting_money: int = 16
    pass_go_reward: int = 1
    stop_on_bankruptcy: bool = True
    
@dataclass(frozen=True)
class GameResult:
    winner: str
    cash_by_player: Dict[str, int]
    position_by_player: Dict[str, str]
    turns_played: int
    turn_log: Optional[List[str]] = None

class Game:
    """Deterministic game engine for a fixed board and roll sequence."""

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

        turns_played = turn_index + 1
        winner = max(self.players, key=lambda player: player.cash).name
        cash_by_player = {player.name: player.cash for player in self.players}
        position_by_player = {
            player.name: self.board.space_at(player.position).name for player in self.players
        }

        return GameResult(
            winner=winner,
            cash_by_player=cash_by_player,
            position_by_player=position_by_player,
            turns_played=turns_played,
            turn_log=turn_log if include_turn_log else None,
        )