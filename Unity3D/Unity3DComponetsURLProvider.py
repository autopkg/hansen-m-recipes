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

__all__ = ["Unity3DComponetsURLProvider"]

DEFAULT_COMPONENT = "Unity"
BASE_URL = "http://netstorage.unity3d.com/unity"
DOWNLOAD_URL = "http://download.unity3d.com/download_unity/"
WHATS_NEW = "http://unity3d.com/unity/whats-new"
UNITY_DOWNLOAD_ARCHIVE = "http://unity3d.com/get-unity/download/archive"

class Unity3DComponetsURLProvider(Processor):
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

        try:
            data = urllib2.urlopen("%s/%s/unity-%s-osx.ini" % (BASE_URL, revision, version))
        except BaseException as err:
            raise ProcessorError(
                "Unexpected error retrieving ini file: '%s'" % err)

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
        """Return the latest revision and version from the release notes"""

        try:
            data = urllib2.urlopen(WHATS_NEW).read()
        except BaseException as err:
            raise ProcessorError(
                "Unexpected error retrieving URL: '%s'" % err)

        # Regex matching expressions
        re_version = re.compile(r'<h2>?(?P<version>[0-9a-z.]+)"? Release Notes \(FULL\)</h2>')
        re_revision = re.compile(r'<p>Revision: ?(?P<revision>[0-9a-z]+)"?</p> ')

        # Search for latest version string.
        version_match = re_version.search(data)
        if not version_match:
            raise ProcessorError("Unable to find latest version string in %s." % WHATS_NEW)

        # Search for latest revision string.
        revision_match = re_revision.search(data)
        if not revision_match:
            raise ProcessorError("Unable to find latest revision string in %s." % WHATS_NEW)

        return (revision_match.group("revision"), version_match.group("version"))


if __name__ == "__main__":
    PROCESSOR = Unity3DCompontentsURLProvider()
    PROCESSOR.execute_shell()
