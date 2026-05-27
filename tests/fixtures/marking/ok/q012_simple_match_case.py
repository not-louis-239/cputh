for i in range(16):
    i_mod_3 = i % 3
    match i_mod_3:
        case 0:
            print("fizz")
        case _:
            print(i)

