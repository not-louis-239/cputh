def build_message(name: str | None) -> str:
    return name if name is not None else "nobody"

def todo_feature() -> None:
    raise NotImplementedError

def main() -> None:
    count = 0

    while True:
        print(f"{count = }")
        count += 1

        if count > 5:
            break

    count -= 1
    print(build_message("charlie"))
    print(build_message(None))

    x = 3
    if x is not 0:
        print(f"x is not 0, x is: {x}")

if __name__ == "__main__":
    main()
