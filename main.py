import argparse

DEFAULT_PLAYER_ORDER = ["Peter", "Billy", "Charlotte", "Sweedal"]

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

if __name__ == "__main__":
	main()
