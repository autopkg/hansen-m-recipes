#!/usr/bin/python
#
# Copyright 2013 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2013-11-12.
# Based on AutoPkg URLProviders by Per Olofsson (per.olofsson@gu.se)

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["FetchURLProvider"]


FETCH_BASE_URL = "http://fetchsoftworks.com/fetch/download/"
re_fetch_dmg = re.compile(r'a href="/fetch/download/?(?P<url>Fetch_.*\.dmg)"?')


class FetchURLProvider(Processor):
    description = "Provides URL to the latest release of Fetch."
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is '%s'." % FETCH_BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest release of Fetch.",
        },
    }
    
    __doc__ = description
    
    def get_fetch_dmg_url(self, base_url):
        # Read HTML index.
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        
        # Search for download link.
        m = re_fetch_dmg.search(html)
        if not m:
            raise ProcessorError("Couldn't find download URL in %s" % base_url)
        
        # Return URL.
        url = FETCH_BASE_URL.rsplit("/", 1)[0] + "/" + m.group("url") + "?direct=1"
        return url
    
    def main(self):
        # Determine base_url.
        base_url = self.env.get('base_url', FETCH_BASE_URL)
        
        self.env["url"] = self.get_fetch_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])
    

if __name__ == '__main__':
    processor = FetchURLProvider()
    processor.execute_shell()
    

