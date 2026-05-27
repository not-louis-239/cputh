import sys

dct = {
  'a': 1,
  'b': 0,
  'c': 3
}

for k, v in dct.items():
    if v is not 0:
        sys.stdout.write(f"{k}: {v}\n")

# in a dictionary comprehension
x = [(k, v) for k, v in dct.items()]
print(x)

lst = [1, 2, 3]
for i, item in enumerate(lst):
    sys.stdout.write(f"{i}. {item}\n")

with open("./file.txt", "r") as file:
    contents = file.read()
    sys.stdout.write(contents)

ints = [-1, -2, 0, 4]
for x in (x for x in ints if x > 0):
    sys.stdout.write(f"{x}\n")
