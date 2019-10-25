#!/usr/bin/env python
""" Run the setup.py tests for BayOTA

"""
import sys
import subprocess
from bayota_util.s3_operations import get_workspace_from_s3
from bayota_settings.base import get_bayota_version


def main():
    # Pull the workspace from s3 into the container
    s3_workspace_dir = 'optimization/ws_copies/bayota_ws_' + get_bayota_version()
    get_workspace_from_s3(log_level='INFO', s3_workspace_dir=s3_workspace_dir)

    # Run the tests
    p1 = subprocess.Popen([f"python /root/bayota/setup.py test"], shell=True)
    p1.wait()
    # Get return code from process
    return_code = p1.returncode
    if p1.returncode != 0:
        raise RuntimeError(f"setup.py tests finished with non-zero code <{return_code}>")


if __name__ == '__main__':
    sys.exit(main())
