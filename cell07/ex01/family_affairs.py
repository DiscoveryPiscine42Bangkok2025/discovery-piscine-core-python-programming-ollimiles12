dupont_family = {
"florian": "red",
"marie": "blond",
"virginie": "brunette",
"david": "red",
"franck": "red"
}

def ind_the_redheads(x):
    result = []
    for i in x:
        if "red" in x[i]:
            z = i
            result.append(z)
    return result


print(ind_the_redheads(dupont_family))