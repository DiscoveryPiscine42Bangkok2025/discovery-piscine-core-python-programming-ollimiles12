from checkmate import checkmate
import sys
def main():
    args = sys.argv[1:] 
    for board_file in args:
        try:
            with open(board_file, 'r') as file:
                text = file.read()
                
            targets = {".", "Q", "B", "R", "P", "K", "q", "b", "r", "p", "k"}

            count = sum(1 for char in text if char in targets)
            
            if count == 16:

                checkmate(text)
            else:
                print("Error")
                
        except FileNotFoundError:
            print("Error")

try:
    if __name__ == "__main__":
        main()
except:
    print("Error")