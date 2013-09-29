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
import sys
import os

sys.path.append('..')
import editparser

tests_folder = os.path.dirname(os.path.abspath(__file__))
edl_file = 'sample.edl'
edl_path = os.path.join(tests_folder, edl_file)
complex_edl_path = os.path.join(tests_folder, 'sample.complex.edl')


class Test_CMX3600(unittest.TestCase):

    def test_nonexisting_edl_path(self):
        with self.assertRaises(IOError):
            editparser.parse(os.path.join(tests_folder, 'this.does.not.exist.edl'))

    def test_complex_parsing(self):
        edl = editparser.parse(complex_edl_path, format='cmx3600')
        self.assertEquals(len(edl.getAllEdits()), 20)
        self.assertEquals(edl.title(), '** V799 SAMPLE LOCK EDIT (3-23-07)')
        a_edit = edl.getEdit(5)
        self.assertEquals(a_edit.get('number'), 4)
        self.assertEquals(a_edit.get('from_clip_name'), '7-2B.NEW.01')
        self.assertEquals(a_edit.get('to_clip_name'), '7-6A.NEW.01')
        self.assertEquals(a_edit.get('blend_dissolve'), True)
        self.assertEquals(a_edit.mediaIn(), editparser.TimeCode('07:07:49:10', base=25))
        self.assertEquals(a_edit.mediaOut(), editparser.TimeCode('07:07:51:14', base=25))
        self.assertEquals(a_edit.globalIn(), editparser.TimeCode('01:00:09:01', base=25))
        self.assertEquals(a_edit.globalOut(), editparser.TimeCode('01:00:11:01', base=25))


    def test_basic_parsing(self):
        edl = editparser.parse(edl_path, format='cmx3600')
        self.assertEquals(len(edl.getAllEdits()), 20)
        first_edit = edl.getEdit(0)
        self.assertEquals(first_edit.get('number'), 1)
        self.assertEquals(first_edit.get('tape'), 'L_PREVIE')
        self.assertEquals(first_edit.get('channels'), ['V'])
        self.assertEquals(first_edit.get('transition'), 'C')
        self.assertEquals(first_edit.get('duration'), 0)
        self.assertEquals(first_edit.get('from_clip_name'), 'SC0020_SH010_L_C007_JH')
        self.assertEquals(first_edit.mediaIn(), editparser.TimeCode('00:00:00:01', base=25))
        self.assertEquals(first_edit.mediaOut(), editparser.TimeCode('00:00:29:09', base=25))
        self.assertEquals(first_edit.globalIn(), editparser.TimeCode('01:00:50:00', base=25))
        self.assertEquals(first_edit.globalOut(), editparser.TimeCode('01:01:19:08', base=25))

        #for edit in edl.getAllEdits():
        #    print edit._attributes

class TestArbitraryBase(unittest.TestCase):
    def test_valid_base_parsing(self):
        edl = editparser.parse(edl_path, format='cmx3600', base=30)
        edit = edl.getEdit(0)
        self.assertEquals(edit.globalIn().base(), 30)

if __name__ == '__main__':
    unittest.main()
