women_scientists = {
"ada": { "name": "Ada Lovelace", "date_of_birth": "1815" },
"cecilia": { "name": "Cecila Payne", "date_of_birth": "1900" },
"lise": { "name": "Lise Meitner", "date_of_birth": "1878" },
"grace": { "name": "Grace Hopper", "date_of_birth": "1906" }
}


def ind_the_redheads(x):
    for i in x:
        name = x[i]["name"]
        dob = x[i]["date_of_birth"]
        print(f"{name} is a great scientist born in {dob}")


ind_the_redheads(women_scientists)
