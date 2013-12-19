#!/usr/bin/python
#
# Copyright 2013 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2013-12-19.
# Based on AutoPkg URLProviders by Per Olofsson (per.olofsson@gu.se)

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["SoundStudioURLProvider"]


SoundStudio_SEARCH_URL = "http://felttip.com/ss/downloads.html"
SoundStudio_BASE_URL = "http://felttip.com/downloads/"
re_SoundStudio_dmg = re.compile(r'a href="/downloads/?(?P<url>sound_studio_.*\.zip)"?')


class SoundStudioURLProvider(Processor):
    description = "Provides URL to the latest release of SoundStudio."
    input_variables = {
        "search_url": {
            "required": False,
            "description": "Default is '%s'." % SoundStudio_SEARCH_URL,
        },        
        "base_url": {
            "required": False,
            "description": "Default is '%s'." % SoundStudio_BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest release of SoundStudio.",
        },
    }
    
    __doc__ = description
    
    def get_SoundStudio_dmg_url(self, search_url):
        # Read HTML index.
        try:
            f = urllib2.urlopen(search_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (search_url, e))
        
        # Search for download link.
        m = re_SoundStudio_dmg.search(html)
        if not m:
            raise ProcessorError("Couldn't find download URL in %s" % search_url)
        
        # Return URL.
        url = SoundStudio_BASE_URL.rsplit("/", 1)[0] + "/" + m.group("url")
        return url
    
    def main(self):
        # Determine base_url.
        search_url = self.env.get('search_url', SoundStudio_SEARCH_URL)
        base_url = self.env.get('base_url', SoundStudio_BASE_URL)
        
        self.env["url"] = self.get_SoundStudio_dmg_url(search_url)
        self.output("Found URL %s" % self.env["url"])
    

if __name__ == '__main__':
    processor = SoundStudioURLProvider()
    processor.execute_shell()
    

