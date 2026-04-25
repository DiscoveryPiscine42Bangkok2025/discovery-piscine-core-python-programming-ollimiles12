import sys
s = len(sys.argv)
if s > 1:
    n = sys.argv[::]
    del n[0]
    for i in n[::-1]:
        print(i)
else:
    print("none")