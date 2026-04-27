from checkmate import checkmate

def main():
    board = """\
R...
...K
..Q.
....\
"""
    checkmate(board)
try:
    if __name__ == "__main__":
        main()
except:
    print("Error")