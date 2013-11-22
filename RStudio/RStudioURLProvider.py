#!/usr/bin/python
#
# Copyright 2013 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2013-11-12.
# Based on AutoPkg URLProviders by Per Olofsson (per.olofsson@gu.se)

import re
import urllib2
from xml.dom import minidom

from autopkglib import Processor, ProcessorError


__all__ = ["RStudioURLProvider"]


RSTUDIO_BASE_URL = "http://download1.rstudio.org"
re_rstudio_dmg = re.compile(r'(?P<url>RStudio-.*\.dmg)"?')


class RStudioURLProvider(Processor):
    description = "Provides URL to the latest release of RStudio."
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is '%s'." % RSTUDIO_BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest release of RStudio.",
        },
    }
    
    __doc__ = description
    
    def get_rstudio_dmg_url(self, base_url):
        # Read HTML index.
        try:
            xmldoc = minidom.parse(urllib2.urlopen(base_url))
            keys = xmldoc.getElementsByTagName('Key')
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
            
        r = []
        for k in keys:
            if ".dmg" in k.toxml():
                r.append(k.firstChild.data)
                
        return base_url + "/" + r[-1]

    def main(self):
        # Determine base_url.
        base_url = self.env.get('base_url', RSTUDIO_BASE_URL)
        
        self.env["url"] = self.get_rstudio_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])
    

if __name__ == '__main__':
    processor = RStudioURLProvider()
    processor.execute_shell()
    

