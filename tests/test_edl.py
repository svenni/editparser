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

from editparser import EDL, Edit, TimeCode


class TestEDLCreation(unittest.TestCase):
    def test_default_creation(self):
        edl = EDL('testEDL', 'edlpath')
        self.assertEquals(edl.title(), 'testEDL')
        self.assertEquals(edl.path(), 'edlpath')
        self.assertEquals(edl.start_tc().tc(), '01:00:00:00')
        self.assertEquals(edl.start_tc().base(), 25)

    def test_custom_timecode_creation(self):
        edl = EDL('testEDL', 'edlpath', startTimeCode='00:00:01:05')
        self.assertEquals(edl.start_tc().tc(), '00:00:01:05')
        self.assertEquals(edl.start_tc().base(), 25)
        self.assertEquals(edl.start_tc().frames(), 30)

    def test_custom_base_creation(self):
        edl = EDL('testEDL', 'edlpath', base=30)
        self.assertEquals(edl.start_tc().tc(), '01:00:00:00')
        self.assertEquals(edl.start_tc().base(), 30)

    def test_custom_timecode_base_creation_ok(self):
        edl = EDL('testEDL', 'edlpath', startTimeCode='00:00:01:05', base=20)
        self.assertEquals(edl.start_tc().tc(), '00:00:01:05')
        self.assertEquals(edl.start_tc().base(), 20)
        self.assertEquals(edl.start_tc().frames(), 25)


class TestEditManagement(unittest.TestCase):
    def setUp(self):
        self.mi = TimeCode('00:00:00:01')
        self.mo = TimeCode('00:00:00:03')
        self.gi = TimeCode('00:00:01:01')
        self.go = TimeCode('00:00:02:01')

        self.edit_c = Edit(self.mi, self.mo, self.gi, self.go)
        self.edit_a = Edit(self.mi, self.mo, self.gi, self.go)
        self.edit_b = Edit(self.mi, self.mo, self.gi, self.go)
        #print self.edit_c

        self.edl = EDL('testEDL', 'edlpath', startTimeCode='00:00:01:05')

    def test_add_edits(self):
        self.assertEquals(len(self.edl.getAllEdits()), 0)
        self.edl.appendEdit(self.edit_a)
        self.edl.appendEdit(self.edit_b)
        self.assertEquals(len(self.edl.getAllEdits()), 2)

    def test_insert_edits(self):
        self.edl.appendEdit(self.edit_a)
        self.assertEquals(self.edl.getAllEdits(), [self.edit_a])
        self.edl.insertEdit(0, self.edit_b)
        self.assertEquals(self.edl.getAllEdits(), [self.edit_b, self.edit_a])

    def test_get_edits(self):
        self.edl.appendEdit(self.edit_a)
        self.edl.appendEdit(self.edit_b)

        self.assertEquals(self.edl.getEdit(0), self.edit_a)

        self.assertIsNone(self.edl.getEdit(8))


if __name__ == '__main__':
    unittest.main()
