import pytest
import os
import subprocess
import json
import itertools
import logging
from colorama import Fore, Back, Style

LOGGER = logging.getLogger(__name__)

@pytest.mark.parametrize(
    "dir",
    [
        pytest.param(it, id=it.name)
        for it in os.scandir("tests/c/patchtests")
        if it.is_dir() and not it.name.startswith(("_", "."))
    ],
)
def test_c_func_equivalence(dir: os.DirEntry[str]):
    # make tmp dir
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    c_compiler = os.getenv("CC", "clang")
    orig_path = os.path.join(dir.path, "orig.c")
    post_path = os.path.join(dir.path, "post.c")
    conf_path = os.path.join(dir.path, "conf.json")
    # compile post.c once WITHOUT env macros defined
    LOGGER.info("compiling post.c")
    subprocess.run([c_compiler, post_path, "-o", "tmp/post"]).check_returncode()
    conf_set = json.load(open(conf_path))
    # [(macro, macro_val), ...] for each macro
    # Ex. [("Foo", "1"), ("Foo", 2)], [("Bar", "2")]
    conf_set_tup_gen = (
        [(macro, macro_val) for macro_val in conf_set[macro]] for macro in conf_set
    )
    for conf_tuple in itertools.product(*conf_set_tup_gen):
        conf = dict(conf_tuple)
        LOGGER.debug( conf)
        # convert all to string and filter out None (which represents undefined macro)
        env_conf = {}
        for k in conf:
            if conf[k] is not None:
                env_conf[k] = str(conf[k])
        # compile orig.c WITH env macros defined
        comp_args = [
            c_compiler,
            orig_path,
            *[f"-D{macro}={conf[macro]}" for macro in env_conf],
            "-o",
            "tmp/orig",
        ]
        LOGGER.info(f"compiling orig.c: {Fore.LIGHTBLACK_EX}{' '.join(comp_args)}{Style.RESET_ALL}")
        subprocess.run(comp_args).check_returncode()
        # run orig (no need for env, since macros are compiled in)
        orig_result = subprocess.run(
            ["./tmp/orig"],
            capture_output=True,
        )
        # run post with env macros
        post_result = subprocess.run(["./tmp/post"], capture_output=True, env=env_conf)
        LOGGER.debug(f"orig out: {Fore.CYAN}{orig_result.stdout}{Style.RESET_ALL}")
        LOGGER.debug(f"post out: {Fore.CYAN}{post_result.stdout}{Style.RESET_ALL}")
        assert orig_result.stdout == post_result.stdout
        assert orig_result.returncode == post_result.returncode
