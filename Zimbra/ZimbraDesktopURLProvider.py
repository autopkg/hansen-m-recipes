#!/usr/bin/python
#
# Copyright 2013 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2013-12-03.
# Based on AutoPkg URLProviders by Per Olofsson (per.olofsson@gu.se)

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["ZimbraDesktopURLProvider"]


ZimbraDesktop_BASE_URL = "http://www.zimbra.com/downloads/zd-downloads.html"
re_ZimbraDesktop_dmg = re.compile(r'href="(?P<url>http://file.\.zimbra\.com/downloads/zdesktop/.*?/.*?/zdesktop_.*_macos_intel.dmg)"')


class ZimbraDesktopURLProvider(Processor):
    description = "Provides URL to the latest release of Zimbra Desktop."
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is '%s'." % ZimbraDesktop_BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest release of Zimbra Desktop.",
        },
    }
    
    __doc__ = description
    
    def get_ZimbraDesktop_dmg_url(self, base_url):
        # Read HTML index.
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        
        # Search for download link.
        m = re_ZimbraDesktop_dmg.search(html)
        if not m:
            raise ProcessorError("Couldn't find download URL in %s" % base_url)
        
        # Return URL.
        url = urllib2.quote(m.group("url"), safe=":/%")
        return url
    
    def main(self):
        # Determine base_url.
        base_url = self.env.get('base_url', ZimbraDesktop_BASE_URL)
        
        self.env["url"] = self.get_ZimbraDesktop_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])
    

if __name__ == '__main__':
    processor = ZimbraDesktopURLProvider()
    processor.execute_shell()
    

