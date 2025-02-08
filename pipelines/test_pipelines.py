from tasks.build_database import execute as build_database


def test_build_database():
    """
    Test the build_database function.

    This function tests the execution of the build_database function from the
    tasks.build_database module. It ensures that the function runs without
    raising any exceptions.
    """
    try:
        build_database()
    except Exception as e:
        assert False, e
    assert True
