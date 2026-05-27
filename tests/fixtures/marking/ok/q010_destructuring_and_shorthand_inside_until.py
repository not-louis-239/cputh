# this is a really hard one

loop_var = 0

__start_var__ = [True]
while (__start_var__ and __start_var__.pop()) or not (loop_var >= 5):
    block = f"""
    Fake block with interpolation
    I bet Charlie will throw up on this.
    current loop index is: {loop_var}
    until_it_happens_to_you x >= 10
    """
    print(block)

    import sys
    print(sys)

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

    y = 0
    __start_var__ = [True]
    while (__start_var__ and __start_var__.pop()) or not (y > 3):
        y += 1

    loop_var += 1
