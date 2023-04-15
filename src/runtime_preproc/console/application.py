#!/usr/bin/env python

from runtime_preproc.console.run_command import RunCommand

from cleo.application import Application

def main() -> int:
    application = Application()
    application.add(RunCommand())
    exit_code: int = application.run()
    return exit_code

if __name__ == "__main__":
    main()

