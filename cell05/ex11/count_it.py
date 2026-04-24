import sys

del sys.argv[0]
n = len(sys.argv)

if n > 0: 
    print(n)
else:
    print("none")

print(f"parameters: {n}")

for i in range(n):
    print(f"{sys.argv[i]}:{len(sys.argv[i])}")
