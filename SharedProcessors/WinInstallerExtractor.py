#!/usr/bin/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-02-13.
#
# Extracts the .exe or .msi file using the 7z utility.

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["WinInstallerExtractor"]


class WinInstallerExtractor(Processor):
    description = "Extracts the Windows archive meta-data using 7z."
    input_variables = {
        "exe_path": {
            "required": False,
            "description": "Path to exe or msi, defaults to %pathname%",
        },
        "preserve_paths": {
            "required": False,
            "description": "eXtract archive with full paths, defaults to 'True'",
        },
        "extract_dir": {
            "required": True,
            "description": "Output path for the extracted archive.",
        },
    }
    output_variables = {
    }
    
    __doc__ = description
    
    def main(self):
        
        exe_path = self.env.get('exe_path', self.env.get('pathname'))
        preserve_paths = self.env.get('preserve_paths', 'True')
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        extract_directory = self.env.get('extract_dir', 'ExtractedInstaller')
        verbosity = self.env.get('verbose', 0)

        extract_flag = 'x' if preserve_paths == 'True' else 'e'
        extract_path = "%s/%s" % (working_directory, extract_directory)

        if not os.path.isfile('/usr/local/bin/7z'):
            self.output("7z Utility Not Found: /usr/local/bin/7z")
            sys.exit(1)
        
        self.output("Extracting: %s" % exe_path)
        cmd = ['/usr/local/bin/7z', extract_flag, '-y', '-o%s' % extract_path , exe_path]
        if verbosity > 1:
            subprocess.check_call(cmd)
        else:
            subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        self.output("Extracted Archive Path: %s" % extract_path)

if __name__ == '__main__':
    processor = WinInstallerExtractor()
    processor.execute_shell()
