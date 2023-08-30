import pytest
import os
import subprocess
import json
import itertools


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

    orig_path = os.path.join(dir.path, "orig.c")
    post_path = os.path.join(dir.path, "post.c")
    conf_path = os.path.join(dir.path, "conf.json")
    # compile post.c once
    subprocess.run(["clang", post_path, "-o", "tmp/post"]).check_returncode()
    conf_set = json.load(open(conf_path))
    # [(macro, macro_val), ...] for each macro
    # Ex. [("Foo", "1"), ("Foo", 2)], [("Bar", "2")]
    conf_set_tup_gen = (
        [(macro, macro_val) for macro_val in conf_set[macro]] for macro in conf_set
    )
    for conf_tuple in itertools.product(*conf_set_tup_gen):
        conf = dict(conf_tuple)
        print("conf", conf)
        # compile orig.c
        comp_args = [
            "clang",
            orig_path,
            *[f"-D{macro}={conf[macro]}" for macro in conf if conf[macro] is not None],
            "-o",
            "tmp/orig",
        ]
        print(" ".join(comp_args))
        subprocess.run(comp_args).check_returncode()
        # run orig
        env_conf = {}
        for k in conf:
            if conf[k] is not None:
                env_conf[k] = str(conf[k])
        print("env", env_conf)
        orig_result = subprocess.run(
            ["./tmp/orig"],
            capture_output=True,
        )
        # run post
        post_result = subprocess.run(["./tmp/post"], capture_output=True, env=env_conf)

        assert orig_result.stdout == post_result.stdout
        assert orig_result.returncode == post_result.returncode
