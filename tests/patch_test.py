import pytest
import os
import subprocess
import json
import itertools
import logging
from colorama import Fore, Style
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)
load_dotenv()

def check_patch_equiv(dir: os.DirEntry[str], post_file: str = None):
    c_compiler = os.getenv("CC", "clang")
    orig_path = os.path.join(dir.path, "orig.c")
    post_path = os.path.join(dir.path, "post.c") if post_file is None else post_file
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
        LOGGER.debug(conf)
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
        LOGGER.info(
            f"compiling orig.c: {Fore.LIGHTBLACK_EX}"
            + f"{' '.join(comp_args)}{Style.RESET_ALL}"
        )
        should_fail_assert = False
        if subprocess.run(comp_args).returncode != 0:
            LOGGER.info(
                "compilation failed, checking that post.c fails C assert for same conf"
            )
            should_fail_assert = True
        # run orig (no need for env, since macros are compiled in)
        if not should_fail_assert:
            orig_result = subprocess.run(
                ["./tmp/orig"],
                capture_output=True,
            )
        # run post with env macros
        post_result = subprocess.run(["./tmp/post"], capture_output=True, env=env_conf)
        if should_fail_assert:
            assert post_result.returncode != 0
            assert b"Assertion " in post_result.stderr
            LOGGER.debug(
                f"post stderr: {Fore.YELLOW}{post_result.stderr}{Style.RESET_ALL}"
            )
            continue
        LOGGER.debug(f"orig out: {Fore.CYAN}{orig_result.stdout}{Style.RESET_ALL}")
        LOGGER.debug(f"post out: {Fore.CYAN}{post_result.stdout}{Style.RESET_ALL}")
        assert orig_result.stdout == post_result.stdout
        assert orig_result.returncode == post_result.returncode

def scan_tree_for_test_folder(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            if (not entry.name.startswith(("_", ".")) and
            any(fname == "orig.c" for fname in os.listdir(entry.path))
            ):
                yield entry
            else:
                yield from scan_tree_for_test_folder(entry.path)

@pytest.mark.parametrize(
    "dir",
    [
        pytest.param(it, id=it.path[6:]) # remove "tests/" from path
        for it in scan_tree_for_test_folder("tests/")
    ],
)
def test_c_func_equivalence_patch(dir: os.DirEntry[str]):
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    subprocess.run(
        ["poetry", "run", "rt_preproc", "patch", "-o", "./tmp/out.c", os.path.join(dir.path, "orig.c")],
    ).check_returncode()
    check_patch_equiv(dir, post_file="./tmp/out.c")


# @pytest.mark.parametrize(
#     "dir",
#     [
#       pytest.param(it, id=it.path + "/" + it.name )
#       for it in scan_tree_for_test_folder("tests/")
#     ],
# )
# def test_c_func_equivalence_premade(dir: os.DirEntry[str]):
#     check_patch_equiv(dir)
