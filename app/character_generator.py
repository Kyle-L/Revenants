import json
import random
import math
import string

with open('info/names.json') as f:
  data = json.load(f)

age = random.randrange(20, 90)
age_string = {1: "early", 5: "mid", 9: "late"}[[1, 5, 9][min(range(len([1, 5, 9])), key = lambda i: abs([1, 5, 9][i]-(age % 10)))]] + ' ' + str(int(age / 10) * 10) + 's'
gender = bool(random.getrandbits(1))
pronouns = data['pronouns']['he' if gender==1 else 'she']
first_name = random.choice(data['first_names']['men' if gender==1 else 'women'])
last_name = random.choice(data['last_names'])
occupation = random.choice(data['occupations'])
retired = '' if age < 40 else ('Retired ' if random.randrange(0, 100) < (math.sin(age * 0.0386 + 3.2) * 100 + 100) else '')

print (f'Age: {age}, {age_string}')
print(f'Name: {first_name} {last_name}')
print(f'Pronouns: {pronouns}')
print(f'Occupation: {retired}{occupation}')

print(f'You are {first_name} {last_name}. who is in their {age_string} and a {occupation.lower()} .')