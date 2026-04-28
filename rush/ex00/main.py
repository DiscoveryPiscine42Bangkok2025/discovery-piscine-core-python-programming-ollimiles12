from checkmate import checkmate

def main():
    board = """\
R...
..K.
.BP.
...."""
    checkmate(board)

try:
    if __name__ == "__main__":
        main()
except:
    print("Error")