#!/usr/bin/env python
""" Run the setup.py tests for BayOTA

"""
import sys
import subprocess
from bayota_util.s3_operations import pull_entire_workspace_from_s3


def main():
    """ Pull the entire workspace from s3 into the container """
    pull_entire_workspace_from_s3(log_level='INFO')

    # Run the tests
    p1 = subprocess.Popen([f"python /root/bayota/setup.py test"], shell=True)
    p1.wait()
    # Get return code from process
    return_code = p1.returncode
    if p1.returncode != 0:
        raise RuntimeError(f"setup.py tests finished with non-zero code <{return_code}>")


if __name__ == '__main__':
    sys.exit(main())
