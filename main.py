import argparse
import json
from typing import Dict, List
from src.board import load_board
from src.game import Game, GameConfig, GameResult

DEFAULT_PLAYER_ORDER = ["Peter", "Billy", "Charlotte", "Sweedal"]

def load_rolls(rolls_path: str) -> List[int]:
    with open(rolls_path) as f:
        rolls = json.load(f)
        
    if not isinstance(rolls, list):
        raise ValueError(f"Rolls file '{rolls_path}' must be a list.")
    if any((not isinstance(roll, int) or roll <= 0) for roll in rolls):
        raise ValueError(f"Rolls file '{rolls_path}' must contain positive integer rolls only.")
    return rolls

def result_to_dict(result: GameResult) -> Dict[str, object]:
    game_result_dict: Dict[str, object] = {
        "ranking": result.ranking,
        "cash_by_player": result.cash_by_player,
        "position_by_player": result.position_by_player,
        "turns_played": result.turns_played,
        "turn_log": result.turn_log,
    }

    return game_result_dict

def print_text_results(roll_path: str, result: GameResult) -> None:
    print(f"Game: {roll_path}")
    print(f"Turns played: {result.turns_played}")

    print("Ranking:")
    for cash, players in result.ranking:
        print(f"- ${cash}: {', '.join(players)}")

    print("Final money:")
    for player_name, cash in result.cash_by_player.items():
        print(f"- {player_name}: ${cash}")

    print("Final positions:")
    for player_name, position in result.position_by_player.items():
        print(f"- {player_name}: {position}")

    if result.turn_log:
        print("Turn log:")
        for entry in result.turn_log:
            print(f"- {entry}")

    print()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate deterministic Woven Monopoly games.")
    parser.add_argument("--board", default="board.json", help="Path to board JSON file.")
    parser.add_argument(
        "--rolls",
        action="append",
        required=True,
        help="Path to a rolls JSON file. Provide this flag multiple times to run multiple games.",
    )
    parser.add_argument(
        "--players",
        default=DEFAULT_PLAYER_ORDER,
        nargs="+",
        help="Player names in turn order (space-separated)."
    )
    parser.add_argument("--start-money", type=int, default=16, help="Starting money for each player.")
    parser.add_argument("--pass-go", type=int, default=1, help="Amount received when passing GO.")
    parser.add_argument("--print-turn-log", action="store_true", help="Include per-turn decision log.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    players = args.players
    
    config = GameConfig(
        player_names=players,
        starting_money=args.start_money,
        pass_go_reward=args.pass_go,
    )
    
    all_results: Dict[str, GameResult] = {}
    for roll_path in args.rolls:
        board = load_board(args.board)
        game = Game(board=board, config=config)
        rolls = load_rolls(roll_path)
        
        result = game.play(rolls=rolls)
        all_results[roll_path] = result

        if args.format == "text":
            print_text_results(roll_path=roll_path, result=result)
            
if __name__ == "__main__":
    main()
