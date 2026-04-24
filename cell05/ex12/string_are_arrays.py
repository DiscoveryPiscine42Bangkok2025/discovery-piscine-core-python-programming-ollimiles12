import sys

del sys.argv[0]

if len(sys.argv) > 0:
    n = sys.argv[0]
    extracted_z = [char for char in n if char == 'z']
    print("".join(extracted_z))

else:
    print("none")