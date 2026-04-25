import sys
def downcase_all(text):
    return text.lower()

del sys.argv[0]
n = len(sys.argv)
if n >= 1:
    for i in range(n):
        print(downcase_all(sys.argv[i]))
else:
    print("none")