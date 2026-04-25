def add_one(x):
    x += 1
    print("Inside add_one, value:", x)
    print("After calling add_one, value:", x)

def main():
    value = 5
    print("Before calling add_one, value:", value)

    add_one(value)


if __name__ == "__main__":
    main()