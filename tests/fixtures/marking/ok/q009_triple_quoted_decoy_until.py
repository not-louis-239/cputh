seen = 0

__start_1234__ = [True]
while (__start_1234__ and __start_1234__.pop()) or not (seen >= 1):
    # This block shouldn't be touched
    block = """
    until_it_happens_to_you seen >= 1
    thats_when_you_said:
    """
    seen += 1
    print(block)
