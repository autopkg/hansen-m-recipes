#!/usr/local/autopkg/python
#
# Matt Hansen (mah60@psu.edu) - 16 Feb 2021
# Based on Copier.py by Per Olofsson
# https://github.com/autopkg/autopkg/blob/master/Code/autopkglib/Copier.py
#
"""See docstring for CopyImporter class"""

import glob
import os.path
import shutil

from autopkglib import Processor, ProcessorError

__all__ = ["CopyImporter"]


class CopyImporter(Processor):
    """Imports source_path to destination_path."""

    description = __doc__
    input_variables = {
        "source_path": {
            "required": False,
            "description": (
                "Path to a source file to import. Defaults to %pathname%."
                "This path may also contain basic globbing characters such as "
                "the wildcard '*', but only the first result will be returned."
            ),
        },
        "destination_path": {
            "required": True,
            "description": (
                "Path to destination. This path may be a directory, and the "
                "'basename' of the source_path will be automatically appended."
            )
        },
        "overwrite": {
            "required": False,
            "description": (
                "Whether the destination will be overwritten if necessary. "
                "Uses a boolean value. Defaults to 'False'."
            ),
        },
    }
    output_variables = {
        "copyimporter_summary_result": {
            "description": "Summary of items imported with CopyImporter."
        }
    }

    __doc__ = description

    def copy(self, source_item, dest_item, overwrite=False):
        """Imports source_item to dest_item, overwriting if allowed"""
        # Import file.
        try:
            if not os.path.exists(dest_item) or overwrite:
                shutil.copyfile(source_item, dest_item)
                self.output(f"Imported {source_item} to {dest_item}")

                self.env['copyimporter_summary_result'] = {
                    'summary_text': 'The following items were imported with CopyImporter:',
                    'report_fields': ['Name', 'Version', 'Path'],
                    'data': {
                        'Name': self.env.get("NAME", "Unknown"),
                        'Version': self.env.get("version", "Unknown"),
                        'Path': dest_item
                    }
                }
            else:
                self.output(
                    f"Skipping import as 'overwrite'='{overwrite}' and "
                    f"'destination_path' exists: '{dest_item}'"
                )
        except BaseException as err:
            raise ProcessorError(f"Can't import {source_item} to {dest_item}: {err}")

    def main(self):
        source_path = self.env.get("source_path", self.env.get("pathname"))
        destination_path = self.env.get("destination_path")

        # clear any pre-exising summary result
        if 'copyimporter_summary_result' in self.env:
            del self.env['copyimporter_summary_result']

        try:
            # don't import directories
            if not os.path.exists(source_path) or os.path.isdir(source_path):
                raise ProcessorError(
                    f"source_path '{source_path}' doesn't exist or is a directory"
                )

            # process path with glob.glob
            matches = glob.glob(source_path)
            if len(matches) == 0:
                raise ProcessorError(
                    f"Error processing path '{source_path}' with glob. "
                )
            matched_source_path = matches[0]
            if len(matches) > 1:
                self.output(
                    f"WARNING: Multiple paths match 'source_path' glob '{source_path}':"
                )
                for match in matches:
                    self.output(f"  - {match}")

            if [c for c in "*?[]!" if c in source_path]:
                self.output(
                    f"Using path '{matched_source_path}' matched from "
                    f"globbed '{source_path}'."
                )

            # create necessary subdirectories if needed
            dir_name = os.path.dirname(destination_path)
            if not os.path.exists(dir_name):
                self.output(f"Creating intermediate directory {dir_name}")
                os.makedirs(dir_name)

            # append basename of source_path if destination_path is a directory
            if os.path.isdir(destination_path) or destination_path.endswith('/'):
                destination_path = os.path.join(
                    destination_path, os.path.basename(matched_source_path))

            # do the import
            self.copy(
                matched_source_path,
                destination_path,
                overwrite=self.env.get("overwrite"),
            )
        except BaseException as err:
            raise ProcessorError(f"Can't import {matched_source_path} to {destination_path}: {err}")

if __name__ == "__main__":
    PROCESSOR = CopyImporter()
    PROCESSOR.execute_shell()