from dataclasses import dataclass, field
from typing import Set


@dataclass
class Player:
	"""Mutable game state for one participant."""

	name: str
	cash: int
	position: int = 0
	owned_property_indexes: Set[int] = field(default_factory=set)

	def move(self, steps: int, board_size: int) -> bool:
		"""Moves the player and returns True when GO is passed."""
		if board_size <= 0:
			raise ValueError("Board size must be greater than zero.")

		start_position = self.position
		destination = start_position + steps
		self.position = destination % board_size
		return destination >= board_size

	def credit(self, amount: int) -> None:
		self.cash += amount

	def debit(self, amount: int) -> None:
		self.cash -= amount

	@property
	def is_bankrupt(self) -> bool:
		return self.cash < 0
