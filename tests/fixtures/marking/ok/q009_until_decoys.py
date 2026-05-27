# nested until with strings
outer = 0

__start_var__ = [True]
while (__start_var__ and __start_var__.pop()) or not (outer >= 3):
    message = "until_it_happens_to_you is just text here"

    __start_var__ = [True]
    while (__start_var__ and __start_var__.pop()) or not (outer >= 2):
        outer += 1
        print(message)


seen = 0

__start_var__ = [True]
while (__start_var__ and __start_var__.pop()) or not (seen >= 1):
    # This block shouldn't be touched
    block = """
    until_it_happens_to_you seen >= 1
    thats_when_you_said:
    """
    seen += 1
    print(block)

name = "Charlie"
print(
    f"""
thats_when_you_said:
    hello {name}
until_it_happens_to_you TheWayIAm
"""
)

turns = 0
__start_var__ = [True]
while (__start_var__ and __start_var__.pop()) or not (turns == 1):
    turns += 1

lyrics = """
thats_when_you_said:
    this is still a string
until_it_happens_to_you TheWayIAm
"""

score = 0
__start_var__ = [True]
while (__start_var__ and __start_var__.pop()) or not (score >= 1):
    score += 1
    print(lyrics.strip())