#!/usr/bin/python
#
# Copyright 2013 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2013-12-03.
# Based on AutoPkg URLProviders by Per Olofsson (per.olofsson@gu.se)

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["ExceedOnDemandURLProvider"]


ExceedOnDemand_BASE_URL = "http://connectivity.opentext.com/products/mac-os-x-platforms.aspx"
re_ExceedOnDemand_dmg = re.compile(r'href="(?P<url>http://mimage\.opentext\.com/patches/connectivity/eod8/.*?/.*?/mac/eodclient8-.*\.dmg)"')


class ExceedOnDemandURLProvider(Processor):
    description = "Provides URL to the latest release of Exceed onDemand Client."
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is '%s'." % ExceedOnDemand_BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest release of Exceed onDemand Client.",
        },
    }
    
    __doc__ = description
    
    def get_ExceedOnDemand_dmg_url(self, base_url):
        # Read HTML index.
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        
        # Search for download link.
        m = re_ExceedOnDemand_dmg.search(html)
        if not m:
            raise ProcessorError("Couldn't find download URL in %s" % base_url)
        
        # Return URL.
        url = urllib2.quote(m.group("url"), safe=":/%")
        return url
    
    def main(self):
        # Determine base_url.
        base_url = self.env.get('base_url', ExceedOnDemand_BASE_URL)
        
        self.env["url"] = self.get_ExceedOnDemand_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])
    

if __name__ == '__main__':
    processor = ExceedOnDemandURLProvider()
    processor.execute_shell()
    

