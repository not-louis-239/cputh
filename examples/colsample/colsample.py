def col(code: int) -> str:
    return f"\033[38;5;{code}m"

def main() -> None:
    for i in range(16):
        for j in range(16):
            idx = i * 16 + j
            print(f"{col(idx)}{idx:03}", end=' ')
        print()

if __name__ == "__main__":
    main()
