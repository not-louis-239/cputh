# `get_it_on cputh_this`
# run me

from __future__ import annotations

accent = "\033[94m"
reset = "\033[0m"

def accented(s: str) -> str:
    return accent + s + reset

def sing() -> str:
    return "\n".join([
        "Beautiful is better than ugly.",
        f"Unless ugly is getting more {accented('attention')}.\n",

        "Explicit is better than implicit.",
        f"Say something. {accented('everyone_knows')} is right there.\n",

        "Readability counts.",
        f"{accented('Nothing')} hurts more than spaghetti code.\n",

        "Errors should never pass silently.",
        f"Unless you're feeling {accented('dangerously')}.\n",

        f"In the face of ambiguity, refuse the temptation to guess.",
        f"{accented('how_long')} has {accented('typing.Any')} been going on?\n",

        f"Mutable defaults are coding {accented('dangerously')}.",
        f"{accented('promise_me')} you won't {accented('import *')}.\n",

        f"If the implementation is hard to explain, {accented('we_dont_talk_anymore')}.",
        f"If the implementation is easy to explain, it is {accented('TheWayIAm')}.\n",

        f"Namespaces are a honking great idea.",
        f"You may be tempted to use a {accented('dict')}, but a {accented('class')} is just {accented('one_call_away')}.\n",

        f"But {accented('tell_me_honestly')}: do you keep your namespaces clean?",
        f"{accented('I knew from the start')} you'd use {accented('global')}.",
    ])

if __name__ == "__main__":
    print(sing())
