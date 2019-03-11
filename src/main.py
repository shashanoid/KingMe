""" Main.py
    Script to check to check python version """
import sys


def check_requirements() -> None:
    """
    check_requirements - ensures that the user has the proper python version
        in order to run King Me.
    """
    print("Checking version requirements....")
    if sys.version_info[0] != 3 or sys.version_info[1] < 6:
        print("ERROR! You don't have the minimum version of python required.")
        sys.exit(1)

    print("Version check succeeded.")
    sys.exit(0)


if __name__ == "__main__":
    check_requirements()
