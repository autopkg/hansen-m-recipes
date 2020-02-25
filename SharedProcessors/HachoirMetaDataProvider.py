#!/usr/bin/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-03-10.
# 
# Based on initial investigations done by James Stewart
# https://github.com/jgstew/file-meta-data/blob/master/file_meta_data.py
# 
# Retreives file metadata using the Hachoir metadata library.
# Requires https://bitbucket.org/haypo/hachoir/wiki/hachoir-metadata

from __future__ import absolute_import, print_function

import os
import string
import sys

from autopkglib import Processor, ProcessorError

try:
    import hachoir_core
    import hachoir_core.cmd_line
    import hachoir_metadata
    import hachoir_parser
except ImportError:
    print("""
    Hachoir Modules not installed!

    Install using: 
        `pip install hachoir_core`
        `pip install hachoir_metadata`
        `pip install hachoir_parser`
    """)
    sys.exit(1)



__all__ = ["HachoirMetaDataProvider"]


class HachoirMetaDataProvider(Processor):
    description = "Retreives file metadata using the Hachoir library'"
    input_variables = {
        "file_path": {
            "required": False,
            "description": "Path to the file, defaults to %pathname%",
        },
        "metadata_key": {
            "required": False,
            "description":
                "Metadata key of %file_path% to return the value of"
        },
        "metadata_index": {
            "required": False,
            "description":
                "Index, if multiple values exist for the %metadata_key%"
        },
        "output_var_name": {
            "required": False,
            "description":
                "Output variable, defaults to %metadata_key% or 'version'"
        },
    }
    output_variables = {
    }
    
    __doc__ = description
    
    def getMetaData(self, filepath):
    
        ufilepath = hachoir_core.cmd_line.unicodeFilename(str(filepath))
        parser = hachoir_parser.createParser(ufilepath, filepath)
        
        if not parser:
            self.output("Unable to parse file")
            sys.exit(1)

        try:
            metadata = hachoir_metadata.extractMetadata(parser)
        except HachoirError as err:
            self.output("Metadata extraction error: %s" % err.decode())
            sys.exit(1)
            
        if not metadata:
            self.output("Unable to extract metadata")
            sys.exit(1)
        else:
            return metadata
    
    def main(self):
        
        file_path = self.env.get('file_path', self.env.get('pathname'))
        metadata_key = self.env.get('metadata_key', 'version')
        metadata_index = int(self.env.get('metadata_index', 0))
        verbosity = self.env.get('verbose', 0)

        if not os.path.isfile(file_path):
            self.output("File Not Found: %s" % file_path)
            sys.exit(1)
        
        self.output("Examining: %s" % file_path)        
        meta_data = self.getMetaData(file_path)
        
        if verbosity > 1:
            self.output(meta_data)

        # Find meta data value, given key and index and strip non-printables
        metadata_value = meta_data.get(metadata_key, index=metadata_index)
        metadvalue_str= [x for x in metadata_value if x in string.printable]
        
        if metadvalue_str:
            output_var_name = self.env.get('output_var_name', metadata_key)

            self.env[output_var_name] = metadvalue_str.encode('ascii', 'ignore')
            self.output("Found Metadata: %s = %s" % (metadata_key, metadvalue_str))

if __name__ == '__main__':
    processor = HachoirMetaDataProvider()
    processor.execute_shell()
