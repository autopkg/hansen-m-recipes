#!/usr/local/autopkg/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-03-10.
# Updated for AutoPkg2 & Python3 by Rusty Myers (rzm102@psu.edu) on 2021-04-06.
# 
# Based on initial investigations done by James Stewart
# https://github.com/jgstew/file-meta-data/blob/master/file_meta_data.py
# 
# Retreives file metadata using the Hachoir metadata library.
# Requires https://bitbucket.org/haypo/hachoir/wiki/hachoir-metadata

import os
import string
import sys

from autopkglib import Processor, ProcessorError

try:
    from hachoir.metadata import extractMetadata
    from hachoir.parser import createParser
    
except ImportError:
    print("""
    Hachoir Modules not installed!

    Install using: 
        `sudo /Library/AutoPkg/Python3/Python.framework/Versions/Current/bin/python3 -m pip install --target=/Library/AutoPkg/Python3/Python.framework/Versions/Current/lib/python3.7/site-packages/ --ignore-installed hachoir`
    """)
    sys.exit(1)

__all__ = ["HachoirMetaDataProvider3"]

class HachoirMetaDataProvider3(Processor):
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
        "output_var_name": {"description":
                "Output variable, defaults to 'version'"
        }
    }
    
    
    __doc__ = description
    
    def getMetaData(self, filepath):
        parser = createParser(str(filepath))
        if not parser:
            self.output("Unable to parse file", file=stderr)
            sys.exit(1)
        with parser:
            try:
                metadata = extractMetadata(parser)
            except Exception as err:
                self.output("Metadata extraction error: %s" % err)
                metadata = None
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

        if verbosity > 2:
            self.output("Possible keys:")
            for k in meta_data._Metadata__data:
                if k:
                    # print(k) # print all keys
                    if meta_data.has(k):
                        self.output(f"  key name: `{k}`")

        if verbosity > 1:
            for line in meta_data.exportPlaintext():
                self.output(line)

        # Find meta data value, given key and index and strip non-printables
        metadata_value = meta_data.get(metadata_key, index=metadata_index)
        metadvalue_str = "".join([x for x in metadata_value if x in string.printable])

        if metadvalue_str:
            output_var_name = self.env.get('output_var_name', metadata_key)            
            self.output("Found Metadata: %s = %s" % (output_var_name, metadvalue_str))
            self.env[output_var_name] = metadvalue_str

if __name__ == '__main__':
    processor = HachoirMetaDataProvider3()
    processor.execute_shell()
