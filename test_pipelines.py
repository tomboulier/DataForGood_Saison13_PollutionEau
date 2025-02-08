import os
import subprocess

print(f"Current working directory: {os.getcwd()}")


def test_build_database():
    """
    Test the build_database function.

    This function tests the execution of the build_database function from the
    tasks.build_database module. It ensures that the function runs without
    raising any exceptions.
    """
    try:
        subprocess.run(["uv", "run", "pipelines/run.py", "run", "build_database"])
    except Exception as e:
        assert False, e
    assert True
