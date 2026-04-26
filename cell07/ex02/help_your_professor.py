from statistics import mean

class_3B = {
    "marine": 18,
    "jean": 15,
    "coline": 8,
    "luc": 9
}

class_3C = {
"quentin": 17,
"julie": 15,
"marc": 8,
"stephanie": 13
}

def average(x):
    return mean(x.values())

print(f"Average for class 3B: {average(class_3B)}")
print(f"verage for class 3C: {average(class_3C)}")