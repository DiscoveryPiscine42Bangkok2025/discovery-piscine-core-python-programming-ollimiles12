import sys

del sys.argv[0]
n = len(sys.argv)
if n >= 1:
    for i in range(n):
        word = sys.argv[i]
        if len(word) < 8:
            word = word + 'Z'*(8-len(word))
        elif len(word) == "8":
            word = word
        print(word)
else:
    print("none")
