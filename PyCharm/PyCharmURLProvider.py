#!/usr/bin/python
#
# Copyright 2013 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2013-12-06.
# Based on AutoPkg URLProviders by Per Olofsson (per.olofsson@gu.se)

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["PyCharmURLProvider"]


PyCharm_BASE_URL = "http://www.jetbrains.com/pycharm/download/download_thanks.jsp?os=mac&edition=comm"
re_PyCharm_dmg = re.compile(r'href="(?P<url>http://download\.jetbrains\.com/python/pycharm-community-.*.dmg)"')



class PyCharmURLProvider(Processor):
    description = "Provides URL to the latest release of PyCharm."
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is '%s'." % PyCharm_BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest release of PyCharm.",
        },
    }
    
    __doc__ = description
    
    def get_PyCharm_dmg_url(self, base_url):
        # Read HTML index.
        try:
            f = urllib2.urlopen(base_url)
            
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        
        # Search for download link.
        m = re_PyCharm_dmg.search(html)
        if not m:
            raise ProcessorError("Couldn't find download URL in %s" % base_url)
        
        # Return URL.
        url = urllib2.quote(m.group("url"), safe=":/%")
        return url
    
    def main(self):
        # Determine base_url.
        base_url = self.env.get('base_url', PyCharm_BASE_URL)
        
        self.env["url"] = self.get_PyCharm_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])
    

if __name__ == '__main__':
    processor = PyCharmURLProvider()
    processor.execute_shell()
    

