# Runtime Preproc

## Setup

To get started, install `poetry` and run `poetry install`.

You'll also need to run `git submodule update --init --recursive` if submodule downloads aren't configured on by default.

To set up precommit hooks, run `pre-commit install`.

You can run `poetry shell` to activate the virtualenv for development (and can leave off the `poetry run` part of commands).

## Commands

To see the list of available commands, run `poetry run rt_preproc list`

Examples:
- `poetry run rt_preproc patch ./tests/c/foo/foo.c`
- `poetry run rt_preproc graphviz ./tests/c/foo/foo.c`
- `poetry run pytest` for running tests

## Testing

I'd recommend setting your `CC` environment variable to `tcc` for running tests since we want to compile C files quickly.