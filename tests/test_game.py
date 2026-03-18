import unittest


from main import load_rolls
from src.board import Board, load_board
from src.game import Game, GameConfig
from src.property import Property
from src.tiles import GoTile


class GameRulesTests(unittest.TestCase):
    def test_must_buy_when_landing_on_unowned_property(self) -> None:
        """Player must buy an unowned property when they land on it."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=3, colour="Brown")])
        game = Game(board=board, config=GameConfig(player_names=["P1"], starting_money=10))

        result = game.play([1])

        player = game.players[0]
        landed_property = board.space_at(1)
        self.assertEqual(player.cash, 7)
        self.assertIs(landed_property.owner, player)
        self.assertEqual(result.position_by_player["P1"], "A")

    def test_landing_on_go_awards_configured_amount(self) -> None:
        """Landing on GO should award the configured amount, but only once."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1"], starting_money=10, pass_go_reward=2),
        )

        game.play([1, 1])

        # Turn 1: buy A for 1. Turn 2: pass GO (+2), land on A (owned by self).
        self.assertEqual(game.players[0].cash, 11)

    def test_passing_go_awards_configured_amount(self) -> None:
        """Passing GO should award the configured amount, but only once."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1"], starting_money=10, pass_go_reward=2),
        )

        game.play([1, 2])

        # Turn 1: buy A for 1. Turn 2: pass GO (+2), land on A (owned by self).
        self.assertEqual(game.players[0].cash, 11)

    def test_monopoly_doubles_rent(self) -> None:
        """Player must pay double the rent when landing on a property they don't own and the owner owns all properties of the same colour."""
        board = Board(
            tiles=[
                GoTile(name="GO"),
                Property(name="B1", price=1, colour="Brown"),
                Property(name="B2", price=1, colour="Brown"),
            ]
        )
        game = Game(board=board, config=GameConfig(player_names=["P1", "P2"], starting_money=10))

        game.play([1, 1, 1, 1])

        # P1 buys B1, P2 pays 1 rent on B1, P1 buys B2, P2 pays doubled rent (2) on B2.
        self.assertEqual(game.players[0].cash, 11)
        self.assertEqual(game.players[1].cash, 7)

if __name__ == "__main__":
    unittest.main()