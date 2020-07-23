
from __future__ import absolute_import

import sys
import os
from brewtils import get_connection_info, Plugin
from .client import GithubSummary

__version__ = "1.0.0.dev0"


def main():
    connection_params = get_connection_info(sys.argv[1:])

    username = os.getenv("github_username")
    password = os.getenv("github_password")
    token = os.getenv("github_token")

    Plugin(
        GithubSummary(username=username, password=password, token=token),
        name="github-summary",
        version=__version__,
        **connection_params
    ).run()


if __name__ == "__main__":
    main()