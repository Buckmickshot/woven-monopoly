from dataclasses import dataclass
from typing import Callable, Dict, List

from board import Board
from player import Player

@dataclass(frozen=True)
class GameConfig:
	player_names: List[str]
	starting_money: int = 16
	pass_go_reward: int = 1
	stop_on_bankruptcy: bool = True

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