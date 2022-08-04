#!/usr/local/autopkg/python
# -*- coding: utf-8 -*-

"""
Based on F5transkriptURLProvider.py by Tim Keller
https://github.com/TK5-Tim/its-unibas-recipes/blob/LogitecSync/F5transkript/F5transkriptURLProvider.py

The resulting link should be formatted similary: https://www.megasoftware.net/do_force_download/MEGAX_10.1.8_installer.pkg
"""

from __future__ import absolute_import, print_function
import re
from autopkglib import URLGetter
import sys

try:
    # import for Python 3
    from html.parser import HTMLParser
except ImportError:
    # import for Python 2
    from HTMLParser import HTMLParser

VERSION_URL = "https://www.megasoftware.net/history"
BASE_URL = "https://www.megasoftware.net/do_force_download/MEGAX_"
REGEX = "MEGA\ X\ version\ (\d{2}\.\d\.\d).*macOS"


# __all__ == ["MEGAURLProvider"]


class MEGAURLProvider(URLGetter):
    """Provides a download URL for the latest version of MEGA"""

    description = __doc__
    input_variables = {}
    output_variables = {
        "url": {"description": "URL to latest version"},
        "version": {"description": "The latest version found"},
    }

    def main(self):
        if sys.version_info.major < 3:
            html_source = self.download(VERSION_URL)
        else:
            html_source = self.download(VERSION_URL).decode("utf-8")
        escaped_url = re.search(REGEX, html_source).group(1)
        unescaped_url = HTMLParser().unescape(escaped_url)
        suffix = "_installer.pkg"
        return_url = BASE_URL + unescaped_url + suffix
        self.env["version"] = escaped_url
        self.env["url"] = return_url
        print(
            "MEGAURLProvider: Match found is %s\n"
            "MEGAURLProvider: Unescaped url is: %s\n"
            "MEGAURLProvider: Suffix is: %s\n"
            "MEGAURLProvider: Returning full url: %s "
            % (escaped_url, unescaped_url, suffix, return_url)
        )


if __name__ == "__main__":
    processor = MEGAURLProvider()
    processor.execute_shell()
