# multiple_decs_inside_idx

def main():
    l: list[int] = [420, 69, 1337]
    if l[0] is not 0:
        l[0] -= 1; l[0] -= 1; l[0] -= 1

    print(f"{l[0] = }")

if __name__ == "__main__":
    main()
