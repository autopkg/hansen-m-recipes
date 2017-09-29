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
import HTMLParser
from ConfigParser import SafeConfigParser

from autopkglib import Processor, ProcessorError
from autopkglib.URLTextSearcher import URLTextSearcher

__all__ = ["Unity3DComponetsURLProvider"]

DEFAULT_COMPONENT = "Unity"
DEFAULT_PLATFORM = 'osx'
BASE_URL = "http://netstorage.unity3d.com/unity"
DOWNLOAD_URL = "https://store.unity.com/download"

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
        "platform": {
            "required": False,
            "description": "The OS to return components for, 'mac' or 'win' ."
            "Defaults to '%s'" % (DEFAULT_PLATFORM),
        },
        "search_url": {
            "required": False,
            "description": "The URL to search for the version and revision."
            "Defaults latest from %s" % (DOWNLOAD_URL),
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

        revision, version = self.get_revision_version()
        platform = self.env.get('platform', DEFAULT_PLATFORM)
        ini_url = "%s/%s/unity-%s-%s.ini" % (BASE_URL, revision, version, platform)

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

    def get_latest_search_url(self):
        """Scrapes for the latest search url listed on download link"""

        # Setup CURL_PATH, if not already
        if not 'CURL_PATH' in self.env:
            self.env['CURL_PATH'] = '/usr/bin/curl'

        platform = self.env.get('platform', DEFAULT_PLATFORM)
        re_searchurl = re.compile(r'%s/thank-you\?thank-you=personal&amp;os=%s&amp;nid=[0-9]+' % (DOWNLOAD_URL, platform))

        search_url, smatch_dict = self.get_url_and_search(DOWNLOAD_URL, re_searchurl)

        if not search_url:
            raise ProcessorError("Can't find search_url from %s." % DOWNLOAD_URL)
        else:
            search_url = HTMLParser.HTMLParser().unescape(search_url)
            self.output("Search URL: %s" % search_url)

        return search_url

    def get_revision_version(self):
        """Return the latest revision and version from the download link"""

        search_url = self.env.get('search_url', self.get_latest_search_url())

        # Setup CURL_PATH, if not already
        if not 'CURL_PATH' in self.env:
            self.env['CURL_PATH'] = '/usr/bin/curl'

        # Regex matching expressions
        re_version = re.compile(r'UnityDownloadAssistant-(?P<version>[0-9a-z.]+)?\.[dmg|exe]')
        re_revision = re.compile(r'unity\\/(?P<revision>[0-9a-z]+)"?\\/UnityDownloadAssistant-')

        version, vmatch_dict = self.get_url_and_search(search_url, re_version)
        revision, rmatch_dict = self.get_url_and_search(search_url, re_revision)

        # Search for latest version string.
        if not version:
            raise ProcessorError("Can't find version from %s." % search_url)
        else:
            self.output("Latest Version: %s" % version)

        # Search for latest revision string.
        if not revision:
            raise ProcessorError("Can't find revision from %s." % search_url)
        else:
            self.output("Latest Revision: %s" % revision)

        return (revision, version)


if __name__ == "__main__":
    PROCESSOR = Unity3DCompontentsURLProvider()
    PROCESSOR.execute_shell()
