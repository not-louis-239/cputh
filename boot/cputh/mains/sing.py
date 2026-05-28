from cputh.utils.args import Args
from cputh.compile.compiler import compile_cputh_to_py

def main(args: Args) -> int:
    print('running sing branch...')
    assert args.input is not None

    print(args.input)

    try:
        return 0
    except KeyboardInterrupt:
        return 130
    except BaseException:
        return 1

if __name__ == "__main__":
    main(Args(command="sing"))
