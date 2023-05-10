#!/usr/bin/env python

from rt_preproc.cli.graphviz_cmd import GraphvizCmd
from rt_preproc.cli.patch_cmd import PatchCmd
from rt_preproc.cli.print_cmd import PrintCmd

from cleo.application import Application


def main() -> int:
    application = Application("Runtime Preproc", "dev")
    application.add(PatchCmd())
    application.add(PrintCmd())
    application.add(GraphvizCmd())
    exit_code: int = application.run()
    return exit_code


if __name__ == "__main__":
    main()
