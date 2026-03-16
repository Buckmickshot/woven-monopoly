import json

def load_board(board_path):
    with open(board_path) as f:
        return json.load(f)
    

if __name__ == "__main__":
    board = load_board("board.json")
    print(board)