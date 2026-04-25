def grettings(name=None):
    if name is None:
        print("Hello, nobie stranger.")
    elif isinstance(name, (int, float)):
        print("Error! It was not a name.")
    else:
        print(f"Hello, {name}!")

grettings("Alice")
grettings("Will")
grettings()
grettings(42)