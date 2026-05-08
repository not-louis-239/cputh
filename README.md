# cputh compiler

Simple compiler to compile Charlie Puth source to Python.
Why? Because now you can sing your source code!

`cputh` is a soulful, rhythmic transpiler that converts Charlie Puth lyrics to working Python code. Why use boring keywords like `if` and `while` when you could be demanding `attention` or asking `how_long` your loop has been going on?

Inspired by ArnoldC. Same energy, different discography. Arnold lifts. Charlie cries in falsetto.

Free syntax highlighting extension for VS Code included!

## Mapping

### Imports
- `from_where_we_began` -> `from` (See You Again)
- `get_it_on` -> `import` (Marvin Gaye)

### Conditionals
- `attention` -> `if` (Attention)
- `left_right_left` -> `elif` (album: Nine Track Mind)
- `no_matter_where_you_go` -> `else` (One Call Away)

### Membership, Logical Operators
- `i_still_look_at_you_the_same` -> `is` (Hey Brother)
- `all_up_on_ya` -> `in` (Attention)
- `nothing_left` -> `not` (Dangerously)
- `come_along_with_me` -> `and` (One Call Away)
- `share_our_fears` -> `or` (Changes)

### Loops
- `how_long` -> `while` (How Long)
- `goin_round` -> `for` (Left and Right)
- `we_dont_talk_anymore` -> `break` (We Don't Talk Anymore)
- `move_on` -> `continue` (We Don’t Talk Anymore)
- `slow_it_down` -> `pass` (album: Voicenotes)

### Functions and Classes
- `then_theres_you` -> `class` (Then There’s You)
- `one_call_away` -> `def` (One Call Away)
- `smaller_talks` -> `lambda` (Changes)
- `done_for_me` -> `return` (Done for Me)
- `cheating_on_you` -> `yield` (Cheating on You)

### Scope Management
- `this_whole_world` -> `global` (My Gospel)
- `not_alone` -> `nonlocal` (One Call Away)
- `erase` -> `del` (Left and Right)

### Async Execution
- `i_still_can_hear_you` -> `async` (Changes)
- `it_wont_be_long` -> `await` (One Call Away)

### Exception Handling
- `promise_me` -> `assert` (I'll Be There For You)
- `dangerously` -> `try` (Dangerously)
- `please_forgive_me` -> `except` (I Used to Be Cringe)
- `see_you_again` -> `finally` (See You Again)
- `blame_myself` -> `raise`(Dangerously)

### Constants
- `TheWayIAm` -> `True` (album: Voicenotes)
- `ShouldveKnown` -> `False` (We Don't Talk Anymore)
- `Nothing` -> `None` (One Call Away)

### I/O
- `everyone_knows` -> `print` (My Gospel)
- `tell_me_honestly` -> `input` (How Long)

### Data Structures
- `lightswitch` -> `bool` (Light Switch)
- `memories` -> `list` (Left and Right)
- `mind` -> `dict` (Nine Track Mind)

### Context
- `stay_with_me` -> `with` (Stay)
- `call_me` -> `as` (One Call Away)

## Example

```python
# hello_world.cputh
everyone_knows("Hello, World!")
```

```python
# hello_world.py (compiled output)
print("Hello, World!")
```

Or something slightly more emotionally complex:

```python
# emotional.cputh
x = 5
attention x > 3:
    everyone_knows("I knew from the start")
no_matter_where_you_go:
    everyone_knows("You just want attention")
```

## Development Status

I made this as a joke. It is not affiliated with, endorsed by, or known to Charlie Puth. If something explodes, open an issue (at `https://github.com/not-louis-239/cputh/issues`) — I'll admit it's my fault, but you gotta believe me when I say it only happened once.

## Installation & Usage

1. Clone this repository
2. Run binary: `bin/cputh input.cputh output.py`
3. Run the freshly produced Python code: `python3 output.py`

## Licence

Licensed under the Apache License 2.0. See [LICENCE](./LICENCE) for more details.

**Disclaimer**: Please do not sue Monkey.
