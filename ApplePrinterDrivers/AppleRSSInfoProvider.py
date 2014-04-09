#!/usr/bin/env python
#
# Created by Matt Hansen (mah60@psu.edu) on 4/9/2014.
# Based on SparkleUpdateInfoProvider by Timothy Sutton
#  
# Copyright 2014 The Pennsylvania State University.
#

import urllib2
import re

from xml.etree import ElementTree
from autopkglib import Processor, ProcessorError

__all__ = ["AppleRSSInfoProvider"]

# This feed only contains the 50 most recently published downloads.
# Recipes looking for titles not included in this feed will fail.
DEFAULT_FEED = 'http://rss.support.apple.com/?channel=DOWNLOADS'

class AppleRSSInfoProvider(Processor):
    description = "Provides links from Apple Support RSS feeds."
    input_variables = {
        "input_feed": {
            "required": False,
            "description": "RSS feed URL, defaults to %s" % DEFAULT_FEED
        },
        "title_regex": {
            "required": True,
            "description": "Regex string to match an Apple KB article title."
        },
        "LOCALE": {
            "required": False,
            "description": "Locale to use for Apple knowledgebase link."
        },
    }
    output_variables = {
        "link": {
            "description": "Link to matched knowledgebase article."
        },
    }
    
    __doc__ = description
    
    def get_feed_data(self, url):
        request = urllib2.Request(url=url)
        
        try:
            url_handle = urllib2.urlopen(request)
        except:
            raise ProcessorError("Can't open URL %s" % request.get_full_url())

        data = url_handle.read()
        try:
            xmldata = ElementTree.fromstring(data)
        except:
            raise ProcessorError("Error parsing XML from feed.")
            
        return xmldata.findall("channel/item")
        
    def main(self):
        input_feed = self.env.get("input_feed", DEFAULT_FEED)
        title_regex = self.env.get("title_regex")
        
        items = self.get_feed_data(input_feed)
        
        for item_elem in items:
            title = item_elem.find("title")
            
            if re.match(title_regex, title.text):
                self.env["link"] = item_elem.find("link").text

        if self.env.get("link"):
            if self.env.get("LOCALE"):
                self.env["link"] = "%s?viewlocale=%s" % (self.env["link"], self.env.get("LOCALE"))
        else:
            raise ProcessorError("No match found in feed: %s" % input_feed)

if __name__ == "__main__":
    processor = AppleRSSInfoProvider()
    processor.execute_shell()