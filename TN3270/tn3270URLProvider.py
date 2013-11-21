#!/usr/bin/python
#
# Copyright 2013 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2013-11-12.
# Based on AutoPkg URLProviders by Per Olofsson (per.olofsson@gu.se)

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["tn3270URLProvider"]


TN3270_BASE_URL = "http://www.brown.edu/cis/tn3270/"
re_tn3270_dmg = re.compile(r'a href="?(?P<url>tn3270_X_.*\.dmg)"?')


class tn3270URLProvider(Processor):
    description = "Provides URL to the latest release of tn3270."
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is '%s'." % TN3270_BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest release of tn3270.",
        },
    }
    
    __doc__ = description
    
    def get_tn3270_dmg_url(self, base_url):
        # Read HTML index.
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        
        # Search for download link.
        m = re_tn3270_dmg.search(html)
        if not m:
            raise ProcessorError("Couldn't find download URL in %s" % base_url)
        
        # Return URL.
        url = TN3270_BASE_URL.rsplit("/", 1)[0] + "/" + m.group("url")
        return url
    
    def main(self):
        # Determine base_url.
        base_url = self.env.get('base_url', TN3270_BASE_URL)
        
        self.env["url"] = self.get_tn3270_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])
    

if __name__ == '__main__':
    processor = tn3270URLProvider()
    processor.execute_shell()
    

