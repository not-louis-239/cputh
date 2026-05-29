def main():
    int_value: int = 42069
    negative_int: int = -69420
    big_int: int = 12345678901234567890

    float_value: float = 3.14159265358979
    negative_float: float = -0.0001234
    nan_value: float = float("nan")
    inf_value: float = float("inf")

    str_value: str = "string"
    unicode_value: str = "🔥 café π λ 🚀"

    foo = [1, 2, 3, 4, 5]
    bar = {"a": 1, "b": 2}
    baz = (1, 2, 3)

    class Test:
        value = 1337

        def __repr__(self):
            return "TestRepr"

        def __str__(self):
            return "TestStr"

        def __format__(self, spec):
            return f"<formatted:{spec}>"

    obj = Test()

    width = 10
    precision = 4

    # Basic
    print(f"{int_value}")
    print(f"{float_value}")
    print(f"{str_value}")

    # Integer formatting
    print(f"{int_value:d}")
    print(f"{int_value:06d}")
    print(f"{int_value:+d}")
    print(f"{negative_int:+d}")
    print(f"{int_value: }")
    print(f"{int_value:b}")
    print(f"{int_value:o}")
    print(f"{int_value:x}")
    print(f"{int_value:X}")
    print(f"{int_value:#b}")
    print(f"{int_value:#o}")
    print(f"{int_value:#x}")
    print(f"{big_int:_}")
    print(f"{big_int:,}")

    # Alignment / fill
    print(f"{int_value:<10}")
    print(f"{int_value:>10}")
    print(f"{int_value:^10}")
    print(f"{int_value:_<10}")
    print(f"{int_value:*>10}")
    print(f"{int_value:.^20}")

    # Float formatting
    print(f"{float_value:f}")
    print(f"{float_value:.2f}")
    print(f"{float_value:.10f}")
    print(f"{float_value:e}")
    print(f"{float_value:E}")
    print(f"{float_value:g}")
    print(f"{float_value:G}")
    print(f"{float_value:%}")
    print(f"{float_value:.2%}")

    # Weird floats
    print(f"{negative_float:+.8f}")
    print(f"{nan_value}")
    print(f"{inf_value}")
    print(f"{-0.0:f}")

    # Dynamic formatting
    print(f"{float_value:{width}.{precision}f}")
    print(f"{int_value:{width}d}")
    print(f"{float_value:.{precision}f}")
    print(f"{int_value:0{width}d}")

    # Strings
    print(f"{str_value:s}")
    print(f"{str_value!r}")
    print(f"{str_value!s}")
    print(f"{str_value:^20}")
    print(f"{str_value:.3}")
    print(f"{unicode_value}")
    print(f"{unicode_value!a}")

    # Collections
    print(f"{foo}")
    print(f"{foo[0]}")
    print(f"{foo[-1]}")
    print(f"{foo[1:4]}")
    print(f"{bar['a']}")
    print(f"{baz}")

    # Expressions
    print(f"{1 + 2}")
    print(f"{2 * 3 + 4}")
    print(f"{(1 + 2) * 3}")
    print(f"{sum(foo)}")
    print(f"{len(foo)}")
    print(f"{min(foo)}")
    print(f"{max(foo)}")
    print(f"{sorted(foo, reverse=True)}")
    print(f"{[x * 2 for x in foo]}")
    print(f"{{x: x*x for x in foo}}")
    print(f"{(x * 3 for x in foo)}")

    # Debug expressions
    print(f"{foo[0] = }")
    print(f"{foo[-1] = }")
    print(f"{int_value = }")
    print(f"{float_value = :.3f}")
    print(f"{str_value = !r}")
    print(f"{1 + 2 = }")
    print(f"{sum(foo) = }")
    print(f"{foo[:] = }")

    # Nested formatting
    print(f"{f'{int_value}'}")
    print(f"{f'{f'{str_value}'}'}")

    # Escaped braces
    print(f"{{")
    print(f"}}")
    print(f"{{{int_value}}}")
    print(f"{{{{{int_value}}}}}")

    # Object formatting
    print(f"{obj}")
    print(f"{obj!r}")
    print(f"{obj!s}")
    print(f"{obj:weird}")

    # Boolean formatting
    print(f"{True}")
    print(f"{False:d}")

    # Complex numbers
    print(f"{3 + 4j}")
    print(f"{complex(1, -2)}")

    # Walrus operator
    print(f"{(x := 123)}")
    print(f"{x}")

    # Lambda
    print(f"{(lambda n: n * 2)(5)}")

    # Conditional expressions
    print(f"{'yes' if int_value > 0 else 'no'}")
    print(f"{'big' if int_value > 10000 else 'small'}")

    # Multiline
    print(f"""
    hello
    {int_value}
    world
    """)

    # Raw f-strings
    print(rf"C:\test\{int_value}\n")

    # Unicode identifiers
    π = 3.14159
    λ = lambda x: x + 1

    print(f"{π}")
    print(f"{λ(5)}")

    # Extremely cursed
    print(f"{[{x: x**2} for x in range(5)]}")
    print(f"{(((((int_value))))):#010x}")
    print(f"{foo[int(str(0))]}")
    print(f"{({1, 2, 3})}")
    print(f"{({1: 2, 3: 4})}")
    print(f"{((1, 2), (3, 4))}")

    # Nested replacement fields
    print(f"{int_value:{width}}")
    print(f"{int_value:{width}d}")
    print(f"{float_value:{width}.{precision}f}")

    # Conversion flags with formatting
    print(f"{obj!r:>20}")
    print(f"{str_value!a:^30}")

    # Empty format spec
    print(f"{int_value:}")
    print(f"{float_value:}")

    # Weird spacing
    print(f"{      int_value      }")
    print(f"{   foo[0]   =   }")

    # More edge cases
    print(f"{[]}")
    print(f"{dict()}")
    print(f"{set()}")
    print(f"{tuple()}")

    # Generator repr
    print(f"{(x for x in range(3))}")

    # Bytes
    print(f"{b'bytes'}")
    print(f"{bytearray(b'abc')}")

    # None
    print(f"{None}")

    # Massive precision
    print(f"{float_value:.50f}")

    # Sign-aware zero padding
    print(f"{negative_int:=+12d}")

    # Alternate forms
    print(f"{255:#X}")
    print(f"{255:#010x}")

    # Percent edge cases
    print(f"{1.0:%}")
    print(f"{0.0001:.10%}")

    # Scientific notation edge cases
    print(f"{1e100:e}")
    print(f"{1e-100:e}")

    # Format spec built from expression
    print(f"{int_value:{'0>10'}}")

    # Nested expression in format spec
    print(f"{float_value:{width}.{precision + 2}f}")

if __name__ == "__main__":
    main()
