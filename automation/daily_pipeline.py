"""Compatibility entry point; executes the same production scan as daily_run."""
from automation.daily_run import run

if __name__ == '__main__':
    run()
