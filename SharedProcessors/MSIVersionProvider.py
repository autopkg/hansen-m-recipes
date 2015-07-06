#!/usr/bin/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-03-16.
# 
# 
# Retreives the version of a .msi file using the lessmsi utility via Wine.

import os
import sys
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["MSIVersionProvider"]

WINE_PATH = '/usr/local/bin/wine'
LESSMSI_PATH = '/Users/Shared/lessmsi-v1/lessmsi.exe'
LESSMSI_FLAGS = 'v'


class MSIVersionProvider(Processor):
    description = "Retreives the version of a .msi file using lessmsi.'"
    input_variables = {
        "msi_path": {
            "required": False,
            "description": "Path to the .msi, defaults to %pathname%",
        },
    }
    output_variables = {
        "version": {
            "description":
                "Version number of %msi_path%.'"
        },
    }
    
    __doc__ = description

    
    def main(self):
        
        WINE = self.env.get('WINE_PATH', WINE_PATH)
        LESSMSI = self.env.get('LESSMSI_PATH', LESSMSI_PATH)
        FLAGS = self.env.get('LESSMSI_FLAGS', LESSMSI_FLAGS)
        
        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        verbosity = self.env.get('verbose', 0)
        
        if not os.path.isfile(WINE):
            self.output("Wine installation not found: %s" % WINE)
            sys.exit(1)
            
        if not os.path.isfile(LESSMSI):
            self.output("lessmsi installation not found: %s" % LESSMSI)
            self.output("Download --> https://github.com/activescott/lessmsi")
            sys.exit(1)
            
        if not os.path.isfile(msi_path):
            self.output("MSI file path not found: %s" % msi_path)
            sys.exit(1)
            
        self.output("Evauluating: %s" % msi_path)
        cmd = [WINE, LESSMSI, FLAGS, msi_path]

        proc = subprocess.Popen(cmd,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()

        if verbosity > 1:
            if stderr:
                self.output('Wine Errors: %s' % stderr)
        
        version = stdout.strip(' \t\n\r')

        self.env['version'] = version.encode('ascii', 'ignore')
        self.output("Found version: %s" % (self.env['version']))

if __name__ == '__main__':
    processor = MSIVersionProvider()
    processor.execute_shell()
