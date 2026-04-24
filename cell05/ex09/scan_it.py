import sys
del sys.argv[0]
n = len(sys.argv)
if n > 1:
    print(n)
else:
    print("none")