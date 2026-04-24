import sys
n = sys.argv[::]
del n[0]
for i in n:
    print(i)