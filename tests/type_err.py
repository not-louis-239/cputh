# Testing if Charlie can see type errors.

def main():
    x: int = "hello"
    print(x)

# error: line 4: Type "Literal['hello']" is not assignable to declared type "int"
#   "Literal['hello']" is not assignable to "int"

if __name__ == "__main__":
    main()
