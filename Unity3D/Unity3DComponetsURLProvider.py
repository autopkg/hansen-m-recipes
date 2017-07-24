#!/usr/bin/python
#
# Copyright 2016 Matt Hansen based on Tim Sutton's PuppetlabsProductsURLProvider
#
# https://github.com/autopkg/recipes/blob/master/Puppetlabs/PuppetlabsProductsURLProvider.py
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for Unity3DComponents class"""

import re
import urllib2
from ConfigParser import SafeConfigParser

from autopkglib import Processor, ProcessorError
from autopkglib.URLTextSearcher import URLTextSearcher

__all__ = ["Unity3DComponetsURLProvider"]

DEFAULT_COMPONENT = "Unity"
BASE_URL = "http://netstorage.unity3d.com/unity"
SEARCH_URL = "https://store.unity.com/download/thank-you?thank-you=update&os=osx&nid=325"

class Unity3DComponetsURLProvider(URLTextSearcher):
    """Extracts a URL for a Unity3D Component."""
    description = __doc__
    input_variables = {
        "component_name": {
            "required": False,
            "description":
                "Component to fetch URL for. One of 'Unity', 'Documentation', "
                "'StandardAssets', 'Example', 'Android', 'iOS', 'AppleTV', "
                "'Linux', 'Samsung-TV', 'Tizen', 'WebGL', 'Windows'. "
                "Defaults to %s" % (DEFAULT_COMPONENT),
        },
        "search_url": {
            "required": False,
            "description": "The URL to search for the version and revision."
            "Defaults to %s" % (SEARCH_URL),
        },
    }
    output_variables = {
        "title": {
            "description": "Title of the component.",
        },
        "description": {
            "description": "Version of the compontent.",
        },
        "url": {
            "description": "Download URL of the component.",
        },
        "md5": {
            "description": "MD5 the component download.",
        },
        "install": {
            "description": "Is component installed by default, true or false.",
        },
        "mandatory": {
            "description": "Is compontent mandatory for Unity 3D installation.",
        },
        "size": {
            "description": "Size of downloaded component.",
        },
        "installedsize": {
            "description": "Installed size of component.",
        },
        "version": {
            "description": "Version of the compontent.",
        },
    }

    def main(self):
        """Return a download URL and info for a Unity3D component"""

        revision, version = self.get_latest_version()
        ini_url = "%s/%s/unity-%s-osx.ini" % (BASE_URL, revision, version)

        try:
            data = urllib2.urlopen(ini_url)
        except BaseException as err:
            raise ProcessorError(
                "Unexpected error retrieving ini: %s - %s" % (err, ini_url))

        parser = SafeConfigParser()
        parser.readfp(data)

        component_name = self.env.get('component_name', DEFAULT_COMPONENT)

        for key, value in parser.items(component_name):
            if key == 'url':
                self.env['url'] = "%s/%s/%s" % (BASE_URL, revision, value)
            else:
                self.env[key] = value

            self.output("%s: %s = %s" % (component_name, key, self.env.get(key)))

    def get_latest_version(self):
        """Return the latest revision and version from the download link"""

        search_url = self.env.get('search_url', SEARCH_URL)

        # Setup CURL_PATH, if not already
        if not 'CURL_PATH' in self.env:
            self.env['CURL_PATH'] = '/usr/bin/curl'

        # Regex matching expressions
        re_version = re.compile(r'UnityDownloadAssistant-(?P<version>[0-9a-z.]+)?\.dmg')
        re_revision = re.compile(r'unity\\/(?P<revision>[0-9a-z]+)"?\\/UnityDownloadAssistant-')

        version, vmatch_dict = self.get_url_and_search(search_url, re_version)
        revision, rmatch_dict = self.get_url_and_search(search_url, re_revision)

        # Search for latest version string.
        if not version:
            raise ProcessorError("Can't find version from %s." % SEARCH_URL)
        else:
            self.output("Latest Version: %s" % version)

        # Search for latest revision string.
        if not revision:
            raise ProcessorError("Can't find revision from %s." % SEARCH_URL)
        else:
            self.output("Latest Revision: %s" % revision)

        return (revision, version)


if __name__ == "__main__":
    PROCESSOR = Unity3DCompontentsURLProvider()
    PROCESSOR.execute_shell()
