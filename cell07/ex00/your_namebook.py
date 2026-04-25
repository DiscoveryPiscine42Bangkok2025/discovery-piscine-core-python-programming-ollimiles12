persons = {
"jean": "valjean",
"grace": "hopper",
"xavier": "niel",
"fifi": "brindacier"
}

def array_of_names(x):
    result = []
    for i in x:
        z = i + " " + x[i]
        result.append(z.title())
    return result


print(array_of_names(persons))