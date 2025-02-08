import subprocess
import sys


def test_build_database():
    """
    Test the build_database function.

    This function tests the execution of the build_database function from the
    pipelines/run.py script. It ensures that the function runs without raising any exceptions.
    """
    process = subprocess.run(["uv", "run", "pipelines/run.py", "run", "build_database"])

    assert process.returncode == 0, "build_database script failed"
