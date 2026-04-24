import sys

args = sys.argv[1:]
n = len(args)

if n >= 2:
    start = int(args[0])
    end = int(args[1])
    
    result = list(range(start, end + 1))
    print(result)
else:
    print("none")