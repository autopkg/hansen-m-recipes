#!/usr/bin/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-02-13.
#
# Extracts the .exe or .msi file using the 7z utility.

from __future__ import absolute_import

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
        "exe_version_label": {
            "required": False,
            "description": "Name of the value to extract from exe, defaults to \"ProductVersion: \"",
        },
        "preserve_paths": {
            "required": False,
            "description": "eXtract archive with full paths, defaults to 'True'",
        },
        "extract_dir": {
            "required": False,
            "description": "Output path for the extracted archive.",
        },
        "ignore_pattern": {
            "required": False,
            "description": "Wildcard pattern to ignore files from the archive.",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the extraction.",
        },
        "sevenzip_path": {
            "required": False,
            "default": "/usr/local/bin/7z",
            "description": "Path to 7-Zip binary. Defaults to /usr/local/bin/7z."
        }
    }
    output_variables = {
        "version": {
            "required": False,
            "description": "ProductVersion of exe."
        }
    }

    __doc__ = description

    def main(self):

        exe_path = self.env.get('exe_path', self.env.get('pathname'))
        preserve_paths = self.env.get('preserve_paths', 'True')
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        extract_directory = self.env.get('extract_dir', 'ExeExtract')
        ignore_pattern = self.env.get('ignore_pattern', '')
        ignore_errors = self.env.get('ignore_errors', 'False')
        verbosity = self.env.get('verbose', 0)
        exe_version_label = self.env.get('exe_version_label', 'ProductVersion: ')

        extract_flag = 'x' if preserve_paths == 'True' else 'e'
        extract_path = "%s/%s" % (working_directory, extract_directory)

        self.output("Extracting: %s" % exe_path)
        cmd = [self.env['sevenzip_path'], extract_flag, '-y', '-o%s' % extract_path , exe_path]

        if ignore_pattern:
            cmd.append('-x!%s' % ignore_pattern)

        try:
            if verbosity > 1:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                for line in result.stdout.split('\n'):
                    self.output(line)
                    if exe_version_label in line:
                        self.env['version'] =  line.split()[-1]
                        self.output("Found Version: %s" % (self.env['version']))
                        break
            else:
                cmd_output = subprocess.check_output(cmd)
        except:
            if ignore_errors != 'True':
                raise

        self.output("Extracted Archive Path: %s" % extract_path)

if __name__ == '__main__':
    processor = WinInstallerExtractor()
    processor.execute_shell()
