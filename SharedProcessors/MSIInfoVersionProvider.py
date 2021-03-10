#!/usr/local/autopkg/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-03-16.
#
#
# Retreives the version of a .msi file using the msiinfo binary.
# Requires installation of msitools, and availablility of 'msiinfo'
# Run: brew install msitools - https://wiki.gnome.org/msitools

from __future__ import absolute_import

import os
import subprocess
import sys

from autopkglib import Processor, ProcessorError

__all__ = ["MSIInfoVersionProvider"]


class MSIInfoVersionProvider(Processor):
    description = "Retreives the version of a .msi file using msiinfo.'"
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

        MSIINFO = os.path.abspath("/usr/local/bin/msiinfo")
        # LESSMSI = os.path.join(os.path.dirname(os.path.abspath(__file__)),'lessmsi/lessmsi.exe')

        msi_path = self.env.get('msi_path', self.env.get('pathname'))
        verbosity = self.env.get('verbose', 0)

        if subprocess.call(["type", MSIINFO], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
            self.output("msiinfo executable not found at %s" % MSIINFO)
            raise ProcessorError(
                f"MSIInfoVersionProvider: msiinfo executable not found. Need to install using `brew install msitools`"
            )
            sys.exit(1)

        if not os.path.isfile(msi_path):
            self.output("MSI file path not found: %s" % msi_path)
            sys.exit(1)

        self.output("Evauluating: %s" % msi_path)
        cmd = [MSIINFO, 'export', msi_path, 'Property']
        # self.output(" ".join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()

        version = ""
        # self.output(stdout)
        for line in stdout.decode().split("\n"):
            if line.startswith("ProductVersion"):
                version = line.split("\t")[1].strip("\r")
        if verbosity > 1:
            if stderr:
                self.output('msiinfo Errors: %s' % stderr)
        if version == "":
            self.output("Could not find version in msi file. Please open a bug.")
        self.env['version'] = version
        self.output("Found version: %s" % (self.env['version']))

if __name__ == '__main__':
    processor = MSIInfoVersionProvider()
    processor.execute_shell()
