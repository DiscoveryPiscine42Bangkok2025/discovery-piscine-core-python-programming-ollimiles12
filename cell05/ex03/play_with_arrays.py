numbers = [2, 8, 9, 48, 8, 22, -12, 2]
two = [x + 2 for x in numbers if x > 5]
my_list = list(set(two))
print(numbers)
print(my_list)