import sys

del sys.argv[0]
n = len(sys.argv)

if n > 1: 
    n = len(sys.argv)
for i in range(n):
    if "ism" in sys.argv[i]:
        print("",end="")
    else:
        print(sys.argv[i] + "ism")
if n < 1:
    print("none")
