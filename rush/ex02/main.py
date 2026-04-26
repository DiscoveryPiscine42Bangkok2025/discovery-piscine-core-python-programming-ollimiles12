from checkmate import best_move

def main():
    board = """\
R...
...K
..P.
....\
"""
    best_move(board)
try:
    if __name__ == "__main__":
        main()
except:
    print("Error")