import sys
z = len(sys.argv)

if len(sys.argv) != 2:
    print("none")
else:
    n = sys.argv[1]
    s = input("What was the parameter? ")
    if n == s:
        print("Good Job!")
    else:
        print("Nope, sorry...")