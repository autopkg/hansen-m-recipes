#!/usr/bin/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-03-16.
#
#
# Retreives the version of a .msi file using the lessmsi utility via Wine.
# Requires installation of Wine, and availablility of 'wine' in PATH

from __future__ import absolute_import

import os
import subprocess
import sys

from autopkglib import Processor, ProcessorError

__all__ = ["MSIVersionProvider"]


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
        self.output("This processor is depreciated and should not be used. Switch to MSIInfoVersionProvider")
        sys.exit(1)
        LESSMSI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'lessmsi/lessmsi.exe')

        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        verbosity = self.env.get('verbose', 0)

        if subprocess.call(["type", "wine"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
            self.output("wine executable not found.")
            sys.exit(1)

        if not os.path.isfile(msi_path):
            self.output("MSI file path not found: %s" % msi_path)
            sys.exit(1)

        self.output("Evauluating: %s" % msi_path)
        cmd = ['wine', LESSMSI, 'v', msi_path]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
