# a boring regular do-until first
a = 0
__start_1234__ = [True]
while (__start_1234__ and __start_1234__.pop()) or not (a == 5):
    a += 1
    print(f"{a = }")

# edge case: multiline condition
x = 0
y = 0
__start_1234__ = [True]
while (__start_1234__ and __start_1234__.pop()) or not (
    x >= 10 or y >= 6
):
    x += 1
    y += 1; y += 1; y += 1
