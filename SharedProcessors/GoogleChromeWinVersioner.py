#!/usr/bin/python
#
# Copyright 2018 The Pennsylvania State University.
#
# Updated by Rusty Myers (rzm102@psu.edu)
# Modified original by Matt Hansen (mah60@psu.edu).
# Based on WinInstallerExtractor


from __future__ import absolute_import

import re
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["GoogleChromeWinVersioner"]


class GoogleChromeWinVersioner(Processor):
    description = "Extracts the Google Chrome Win version using 7z and Regex."
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
        "ignore_pattern": {
            "required": False,
            "description": "Wildcard pattern to ignore files from the archive.",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the extraction.",
        },
        "output_var_name": {
            "required": False,
            "description":
                "Output variable name. Defaults to 'version'",
        },"version_regex": {
            "required": False,
            "description":
                "Regex statement to override default."
        },
        "sevenzip_path": {
            "required": False,
            "default": "/usr/local/bin/7z",
            "description": "Path to 7-Zip binary. Defaults to /usr/local/bin/7z."
        }
    }
    output_variables = {
        "version": {
            "description":
                "The version of Google Chrome within MSI."
        },
    }

    __doc__ = description

    def main(self):

        exe_path = self.env.get('exe_path', self.env.get('pathname'))
        preserve_paths = self.env.get('preserve_paths', 'True')
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        extract_directory = self.env.get('extract_dir', 'ExtractedInstaller')
        ignore_pattern = self.env.get('ignore_pattern', '')
        ignore_errors = self.env.get('ignore_errors', 'False')
        output_var_name = self.env.get('output_var_name', 'version')
        version_regex = self.env.get('version_regex', '[0-9]{1,2}.[0-9].[0-9]{4}.[0-9]{2,4}')
        verbosity = self.env.get('verbose', 0)

        extract_flag = 'x' if preserve_paths == 'True' else 'e'
        extract_path = "%s/%s" % (working_directory, extract_directory)

        self.output("Extracting: %s" % exe_path)
        cmd = [self.env['sevenzip_path'], extract_flag, '-y', '-o%s' % extract_path , exe_path]

        if ignore_pattern:
            cmd.append('-x!%s' % ignore_pattern)

        try:
            if verbosity > 1:
                subprocess.check_call(cmd)
            else:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise

        self.output("Extracted Archive Path: %s" % extract_path)

        pattern = re.compile(version_regex)

        with open(extract_path + "/[5]SummaryInformation") as file:
            data = file.read()
            msiversion = pattern.findall(data)[0]
        if msiversion != "":
            self.env[output_var_name] = msiversion
        else:
            self.output("Unable to get version from MSI")
            return None


if __name__ == '__main__':
    processor = GoogleChromeWinVersioner()
    processor.execute_shell()
