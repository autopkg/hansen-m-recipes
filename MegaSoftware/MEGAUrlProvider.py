#!/usr/local/autopkg/python
# -*- coding: utf-8 -*-

"""
Based on F5transkriptURLProvider.py by Tim Keller
https://github.com/TK5-Tim/its-unibas-recipes/blob/LogitecSync/F5transkript/F5transkriptURLProvider.py

The resulting link should be formatted similary: https://megasoftware.net/do_force_download/MEGA_12.1.2_installer.pkg
"""

from __future__ import absolute_import, print_function
import re
from autopkglib import URLGetter
import sys


VERSION_URL = "https://www.megasoftware.net/history"
BASE_URL = "https://megasoftware.net/do_force_download/MEGA_"
REGEX = "MEGA\s+\d+\s+version\s+(\d+\.\d+\.\d+)"


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
        html_source = self.download(VERSION_URL, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"})
        if isinstance(html_source, bytes):
            html_source = html_source.decode("utf-8")
        
        match = re.search(REGEX, html_source)
        if not match:
            raise ValueError("MEGAURLProvider: Could not find a version on the history page")
        
        version = match.group(1)
        suffix = "_installer.pkg"
        return_url = BASE_URL + version + suffix
        self.env["version"] = version
        self.env["url"] = return_url
        print("MEGAURLProvider: Latest version found:", version)
        print("MEGAURLProvider: Suffix is:", suffix)
        print("MEGAURLProvider: Returning full url:", return_url)

if __name__ == "__main__":
    processor = MEGAURLProvider()
    processor.execute_shell()
