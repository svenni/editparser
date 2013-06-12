# Copyright (c) 2012, Sveinbjorn J. Tryggvason
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above
#    copyright notice, this list of conditions and the following disclaimer.
#
#    Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT,INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

import unittest
import os
import sys

sys.path.append('..')
import editparser
import editparser.vegas as vegas

tests_folder = os.path.dirname(os.path.abspath(__file__))
edl_file = 'sample.vegas.txt'
edl_path = os.path.join(tests_folder, edl_file)


class Test_Vegas_Basic_Parsing(unittest.TestCase):
    def test_basic_parsing(self):
        edl = editparser.parse(edl_path, format='vegas')

class Test_Vegas_Parsing(unittest.TestCase):
    def setUp(self):
        self.edl = editparser.parse(edl_path, format='vegas')

    def test_something(self):
        pass

class Test_Vegas_VegasEDLLine(unittest.TestCase):
    def setUp(self):
        self.line = r'1; 1; 0.0000; 105840.0000; 1.000000; FALSE; FALSE; 0; TRUE; FALSE; VIDEO; "R:\this\is\file.ext"; 0; 0.0000; 5005.0000; 0.0000; 0.0000; 1.000000; 4; 0.000000; 4; 0.000000; 0; -1; 4; 4; 0.000000; FALSE; 0; 0'

    def test_good_parsing(self):
        vegas.VegasEDLLine(self.line)

    def test_wrong_line_length(self):
        line = r'1; 1; 1; 1'
        self.assertRaises(editparser.ParserError, vegas.VegasEDLLine, line)

    def test_get_int_attributes(self):
        vl = vegas.VegasEDLLine(self.line)
        self.assertEquals(vl.ID, 1)
        assert(isinstance(vl.ID, int))

    def test_get_float_attributes(self):
        vl = vegas.VegasEDLLine(self.line)
        self.assertEquals(vl.StartTime, 0.0)
        assert(isinstance(vl.StartTime, float))

    def test_get_bool_attributes(self):
        vl = vegas.VegasEDLLine(self.line)
        self.assertEquals(vl.Locked, False)
        assert(isinstance(vl.Locked, bool))

    def test_get_string_attributes(self):
        vl = vegas.VegasEDLLine(self.line)
        self.assertEquals(vl.FileName, r'R:\this\is\file.ext')
        assert(isinstance(vl.FileName, str))



if __name__ == '__main__':
    unittest.main()