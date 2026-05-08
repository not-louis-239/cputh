# cputh compiler

Simple compiler to compile Charlie Puth source to Python.
Why? Because now you can sing your source code!

`cputh` is a soulful, rhythmic transpiler that converts Charlie Puth lyrics to working Python code. Why use boring keywords like `if` and `while` when you could be demanding `attention` or asking `how_long` your loop has been running?

Inspired by the logic of ArnoldC, but this time with more hair and perfect pitch!

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
- `move_on` -> `continue` (We Don’t Talk Anymore)
- `we_dont_talk_anymore` -> `break` (We Don't Talk Anymore)
- `slow_it_down` -> `pass` (album: Voicenotes)

### Functions and Classes
- `one_call_away` -> `class` (One Call Away)
- `then_theres_you` -> `def` (Then There’s You)
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
- `nine_track_mind` -> `dict` (Nine Track Mind)

### Context
- `stay_with_me` -> `with` (Stay)
- `call_me` -> `as` (One Call Away)

## Development Status

I made this as a joke, but if something explodes, start an issue.

## Installation & Usage

1. Clone this repository
2. Run binary: `bin/cputh input.cputh output.py`
3. Run the freshly produced Python code: `python3 output.py`

## Licence

Apache 2.0. See LICENCE for more details.

**Disclaimer**: This project is not affiliated with Charlie Puth, though we suspect he'd appreciate the variable naming conventions. Please do not sue Monkey.
