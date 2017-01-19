#!/usr/bin/python
# encoding: utf-8
#
# Copyright 2014 The Pennsylvania State University.
#
"""
BESRelevanceProvider.py

Created by Matt Hansen (mah60@psu.edu) on 2014-02-19.

AutoPkg Processor for retreiving relevance data for tasks.
"""

import os
import hashlib
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["BESRelevanceProvider"]

QNA = '/usr/local/bin/QnA'

class BESRelevanceProvider(Processor):
    description = "Retreives arbitrary relevance data using the QnA utility."
    input_variables = {
        "bes_filepath": {
            "required": False,
            "description":
                "Path to a file for relevance data. Defaults to %pathname%."
        },
        "bes_relevance": {
            "required": False,
            "description":
                "A line of relevance to evaluate in QnA and return the result."
        },
        "output_var_name": {
            "required": False,
            "description":
                "Output variable name. Defaults to 'bes_relevance_result'"
        },
    }
    output_variables = {
        "bes_sha1": {
            "description":
                "The resulting file sha1 of the %bes_filepath%."
        },
        "bes_sha1_short": {
            "description":
                "The short end of %bes_sha1% to be used as a display version."
        },
        "bes_size": {
            "description":
                "The resulting file size of the %bes_filepath%."
        },
        "bes_sha256": {
            "description":
                "The resulting file size of the %bes_filepath%."
        },
    }
    __doc__ = description

    def eval_relevance(self, relevance):
        # Evaluate Relevance Expression
        try:
            proc = subprocess.Popen(QNA, bufsize=-1,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            out, err = proc.communicate(relevance)

            output = {}
            for line in out.strip().split('\n'):
                line_split = line.split(': ')
                output[line_split[0]] = ''.join(line_split[1:])

            if output.get('E', None):
                self.output("Relevance Error: {%s} -- %s" %
                            (relevance, output.get('E')))
                return None
            else:
                return output.get('A', None)
        except Exception, error:
            self.output("QnA Error: (%s) -- %s" % (QNA, error))
            return None

    def main(self):
        # Assign BES Console Variables
        bes_filepath = self.env.get("bes_filepath", None)
        bes_relevance = self.env.get("bes_relevance", None)

        if not os.path.isfile(QNA):
            self.output("QnA utility not found at [%s]."
                        "\n\n Run `autopkg install QnA`" % QNA)

        if bes_filepath and os.path.isfile(bes_filepath):

            self.env['bes_sha1'] = hashlib.sha1(file(
                bes_filepath).read()).hexdigest()
            self.env['bes_size'] = str(os.path.getsize(bes_filepath))
            self.env['bes_sha256'] = hashlib.sha256(file(
                bes_filepath).read()).hexdigest()
            self.env['bes_sha1_short'] = str(self.env.get("bes_sha1"))[-5:]

            self.output("bes_sha1 = %s, bes_size = %s, "
                        "bes_sha256 = %s, bes_sha1_short = %s" %
                        (self.env.get("bes_sha1"),
                         self.env.get("bes_size"),
                         self.env.get("bes_sha256"),
                         self.env.get("bes_sha1_short")))

        if bes_relevance:
            output_var_name = self.env.get("output_var_name",
                                           "bes_relevance_result")

            relevance_result = self.eval_relevance(bes_relevance)

            if relevance_result != None:
                self.env[output_var_name] = relevance_result
            elif output_var_name not in self.env:
                self.env[output_var_name] = None

            self.output("%s = %s" %
                        (output_var_name,
                         self.env.get(output_var_name)))

if __name__ == "__main__":
    processor = BESRelevanceProvider()
    processor.execute_shell()
