"""Nuitka / frozen entrypoint (avoid compiling package __main__.py directly)."""

from pytool.win_motw import clear_mark_of_the_web

clear_mark_of_the_web()

from pytool.app import run

if __name__ == "__main__":
    run()
