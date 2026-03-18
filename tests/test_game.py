import unittest
import json
import tempfile
from pathlib import Path

from main import load_rolls, result_to_dict
from src.board import Board, load_board
from src.game import Game, GameConfig
from src.property import Property
from src.tiles import GoTile

class TestInputOutput(unittest.TestCase):

    @staticmethod
    def write_json(path, data):
        with open(path, "w") as f:
            json.dump(data, f)

    def test_load_rolls_valid_and_invalid(self):
        """Only allow loading of rolls from a json that contains a list of non-negative integers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # valid rolls file
            good = tmp_path / "good_rolls.json"
            self.write_json(good, [1, 2, 3])
            self.assertEqual(load_rolls(str(good)), [1, 2, 3])

            # invalid rolls file: not a list
            bad_type = tmp_path / "bad_type.json"
            self.write_json(bad_type, {"not": "a list"})
            with self.assertRaises(ValueError):
                load_rolls(str(bad_type))

            # invalid values in rolls file: non-positive integers
            bad_values = tmp_path / "bad_values.json"
            self.write_json(bad_values, [1, -2, "x"])
            with self.assertRaises(ValueError):
                load_rolls(str(bad_values))

    def test_load_board_valid_and_invalid(self):
        """Only allow loading of boards from a json that contains a list of valid dicts representing tiles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # valid minimal board
            good = tmp_path / "good_board.json"
            self.write_json(good, [{"name": "GO", "type": "go"}])
            board = load_board(str(good))
            self.assertIsInstance(board, Board)
            self.assertEqual(board.tile_at(0).name, "GO")

            # invalid board file: not a list
            bad1 = tmp_path / "bad_board_1.json"
            self.write_json(bad1, {"name": "GO"})
            with self.assertRaises(ValueError):
                load_board(str(bad1))

            # first tile not GO
            bad2 = tmp_path / "bad_board_2.json"
            self.write_json(bad2, [
                {"name": "NotGO", "type": "property", "price": 1, "colour": "C"}
            ])
            with self.assertRaises(ValueError):
                load_board(str(bad2))

    def test_result_to_dict_structure(self):
        """Ensure result_to_dict output has expected structure."""
        # simple board
        board = Board(tiles=[
            GoTile(name="GO"),
            Property(name="A", price=1, colour="Brown")
        ])

        game = Game(
            board=board,
            config=GameConfig(player_names=["P1", "P2"], starting_money=5, pass_go_reward=0)
        )

        result = game.play([1, 1])
        out = result_to_dict(result)

        # structure checks
        self.assertIn("winner", out)
        self.assertIn("ranking", out)
        self.assertIsInstance(out["ranking"], list)

        self.assertIn("cash_by_player", out)
        self.assertIsInstance(out["cash_by_player"], dict)

        self.assertIn("position_by_player", out)
        self.assertIsInstance(out["position_by_player"], dict)

        self.assertIn("turns_played", out)

class GameRulesTests(unittest.TestCase):
    def test_players_move_in_correct_order(self) -> None:
        """Players must take turns in the exact input order."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown"), Property(name="B", price=1, colour="Brown")])

        game = Game(
            board=board,
            config=GameConfig(player_names=["P1", "P2", "P3"], starting_money=10),
        )

        # Each roll is unique → reveals order
        game.play([1, 2, 3])

        self.assertEqual(game.players[0].position, 1)  # P1 got roll 1
        self.assertEqual(game.players[1].position, 2)  # P2 got roll 2
        self.assertEqual(game.players[2].position, 0)  # P3 got roll 3

    def test_turn_order_wraps_correctly(self) -> None:
        """Turn order should wrap around to the first player."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1", "P2"], starting_money=10),
        )

        game.play([1, 1, 1])  # P1, P2, P1 again

        self.assertEqual(game.players[0].position, 0)  # P1 moved twice (1 → 0)
        self.assertEqual(game.players[1].position, 1)  # P2 moved once

    def test_default_starting_money_is_16(self) -> None:
        """Players should start with $16 by default."""
        board = Board(tiles=[GoTile(name="GO")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1", "P2"]),
        )

        for player in game.players:
            self.assertEqual(player.cash, 16)

    def test_players_start_on_go_tile(self) -> None:
        """All players should start at position 0 (GO)."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1", "P2"]),
        )

        for player in game.players:
            self.assertEqual(player.position, 0)

        # Also check GO tile explicitly
        self.assertEqual(board.tile_at(0).name, "GO")

    def test_landing_on_go_awards_default_amount_1(self) -> None:
        """Landing on GO should award the default amount which is 1, but only once."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1"], starting_money=10),
        )

        # Turn 1: buy A for 1. Turn 2: land on GO (+1).
        game.play([1, 1])

        self.assertEqual(game.players[0].cash, 10)

    def test_landing_on_go_awards_configured_amount(self) -> None:
        """Landing on GO should award the configured amount, but only once."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1"], starting_money=10, pass_go_reward=2),
        )

        # Turn 1: buy A for 1. Turn 2: land on GO (+2).
        game.play([1, 1])

        self.assertEqual(game.players[0].cash, 11)

    def test_passing_go_awards_configured_amount(self) -> None:
        """Passing GO should award the configured amount, but only once."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1"], starting_money=10, pass_go_reward=2),
        )

        # Turn 1: buy A for 1. Turn 2: pass GO (+2), land on A (owned by self).
        game.play([1, 2])

        self.assertEqual(game.players[0].cash, 11)
    
    def test_no_rent_on_own_property(self) -> None:
        """Player should not pay rent when landing on their own property."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=2, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1"], starting_money=10),
        )

        game.play([1, 2])  # buy, pass Go, then land again

        self.assertEqual(game.players[0].cash, 9)  # only paid once
        self.assertEqual(game.players[0].position, 1)  # landed on A

    def test_must_buy_when_landing_on_unowned_property(self) -> None:
        """Player must buy an unowned property when they land on it."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=3, colour="Brown")])
        game = Game(board=board, config=GameConfig(player_names=["P1"], starting_money=10))

        result = game.play([1])

        player = game.players[0]
        landed_property = board.tile_at(1)
        self.assertEqual(player.cash, 7)
        self.assertIs(landed_property.owner, player)
        self.assertEqual(result.position_by_player["P1"], "A")

    def test_must_pay_rent_when_landing_on_owned_property(self) -> None:
        """Player must pay rent when landing on a property they don't own and owner doesn't own all properties of the same colour."""
        board = Board(
            tiles=[
                GoTile(name="GO"),
                Property(name="B1", price=1, colour="Brown"),
                Property(name="B2", price=1, colour="Brown"),
            ]
        )
        game = Game(board=board, config=GameConfig(player_names=["P1", "P2"], starting_money=10))

        # P1 buys B1 for 1, P2 pays 1 rent on B1.
        game.play([1, 1])

        self.assertEqual(game.players[0].cash, 10)
        self.assertEqual(game.players[1].cash, 9)

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

        # P1 buys B1 for 1, P2 pays 1 rent on B1, P1 buys B2 for 1, P2 pays doubled rent (2) on B2.
        game.play([1, 1, 1, 1])

        self.assertEqual(game.players[0].cash, 11)
        self.assertEqual(game.players[1].cash, 7)

    def test_game_stops_on_first_bankruptcy(self) -> None:
        """Game stops on first player bankruptcy."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=2, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1", "P2"], starting_money=1, pass_go_reward=0),
        )

        # P1 buys A for 2, P1 goes bankrupt (-1).
        result = game.play([1, 1, 1, 1])

        self.assertEqual(result.turns_played, 1)
        self.assertEqual(result.cash_by_player["P1"], -1)

    def test_board_wraps_around(self) -> None:
        """Last tile wraps around to the first tile."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=2, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1"], starting_money=10, pass_go_reward=0),
        )

        # P1 buys A for 2, P1 wraps around to starting tile (GO).
        _ = game.play([1, 1])

        self.assertEqual(game.players[0].position, 0)
    
    def test_multiple_go_passes(self) -> None:
        """Passing GO multiple times in one move should award each time it is passed."""
        board = Board(tiles=[GoTile(name="GO"), Property(name="A", price=1, colour="Brown")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["P1"], starting_money=10, pass_go_reward=2),
        )

        hi = game.play([5], True)  # board size = 2 → wraps multiple times
        
        # Should get +2 for each time GO is passed
        self.assertEqual(game.players[0].cash, 13)

    def test_ranking_tie_sorted_alphabetically(self) -> None:
        """Players with equal cash should be sorted alphabetically within ranking."""
        board = Board(tiles=[GoTile(name="GO")])
        game = Game(
            board=board,
            config=GameConfig(player_names=["B", "A"], starting_money=10),
        )

        # P1 and P2 loop back to starting tile (GO).
        result = game.play([1, 1])

        # Same cash → names sorted
        self.assertEqual(result.ranking[0][1], ["A", "B"])

class IntegrationTests(unittest.TestCase):
    def test_simple_game_with_non_distinct_ranking(self) -> None:
        """Simple game where players end with non-distinct cash values."""
        board = load_board("tests/board_test_1.json")
        rolls = load_rolls("tests/rolls_test_1.json")

        game = Game(
            board=board,
            config=GameConfig(player_names=["P1", "P2", "P3", "P4"], starting_money=10, pass_go_reward=0),
        )

        result = game.play(rolls)

        self.assertEqual(result.cash_by_player, {
            "P1": 8,  # +2 -2
            "P2": 6,
            "P3": 12,
            "P4": 8,
        })

        self.assertEqual(result.ranking, [
            (12, ["P3"]),
            (8, ["P1", "P4"]),
            (6, ["P2"]),
        ])

        self.assertEqual(result.position_by_player, {
            "P1": "B",
            "P2": "B",
            "P3": "B",
            "P4": "C",
        })

    def test_simple_game_with_double_rent(self) -> None:
        """Game where players own all properties of same colour."""
        board = load_board("tests/board_test_2.json")
        rolls = load_rolls("tests/rolls_test_2.json")

        game = Game(
            board=board,
            config=GameConfig(player_names=["P1", "P2", "P3"], starting_money=10, pass_go_reward=0),
        )

        result = game.play(rolls)

        self.assertEqual(result.cash_by_player, {
            "P1": 8,
            "P2": 16,
            "P3": 2,
        })

        self.assertEqual(result.ranking, [
            (16, ["P2"]),
            (8, ["P1"]),
            (2, ["P3"]),
        ])

        self.assertEqual(result.position_by_player, {
            "P1": "B",
            "P2": "GO",
            "P3": "B",
        })

if __name__ == "__main__":
    unittest.main()