DEFAULT_STATE = 0b0

F_MARVIN_GAYE = 0b1

def add_flag(state: int, *, f: int) -> int:
    """Sets a flag in the state to 1 and returns the new state."""
    return state | f

def rm_flag(state: int, *, f: int) -> int:
    """Sets a flag in the state to 0 and returns the new state."""
    return state & ~f

def flag_is_active(state: int, *, f: int) -> bool:
    """Returns 1 if the flag is active in the state, 0 otherwise."""
    return (state & f) != 0

def _test():
    TEST_FLAG_1 = 0b1
    TEST_FLAG_2 = 0b10
    TEST_FLAG_3 = 0b100
    STARTING_TEST_STATE = 0b110

    state = STARTING_TEST_STATE
    print(f"Starting state: {state:04b}")

    state = add_flag(state, f=TEST_FLAG_1)
    print(f"State after adding TEST_FLAG_1: {state:04b}")
    state = rm_flag(state, f=TEST_FLAG_2)
    print(f"State after removing TEST_FLAG_2: {state:04b}")
    flag_3_is_active = flag_is_active(state, f=TEST_FLAG_3)
    print(f"TEST_FLAG_3 is active in the state: {flag_3_is_active}")

if __name__ == "__main__":
    _test()
