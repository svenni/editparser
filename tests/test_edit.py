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

from editparser import Edit, TimeCode, EditError


class TestEditCreation(unittest.TestCase):

    def test_creation_from_string_input(self):
        Edit('00:00:00:01', '00:00:00:02', '00:00:01:01', '00:00:02:01')

    def test_creation_from_TC_input(self):
        mi = TimeCode('00:00:00:01')
        mo = TimeCode('00:00:00:03')
        gi = TimeCode('00:00:01:01')
        go = TimeCode('00:00:02:01')

        Edit(mi, mo, gi, go)

    def test_creation_from_mixed_input(self):
        mi = TimeCode('00:00:00:01')
        mo = '00:00:00:03'
        gi = '00:00:01:01'
        go = TimeCode('00:00:02:01')

        Edit(mi, mo, gi, go)

    def test_creation_bad_obj_input(self):
        with self.assertRaises(RuntimeError):
            Edit([], {}, [], [])

    def test_creation_bad_string_input(self):
        with self.assertRaises(RuntimeError):
            Edit('abc', 'def', '00:00:02:05', 'stuff')

    def test_global_io_constraint(self):
        mi = TimeCode('00:00:00:01')
        mo = TimeCode('00:00:00:03')
        gi = TimeCode('00:00:01:01')
        go = TimeCode('00:00:02:01')

        Edit(mi, mo, gi, go)

        mi = TimeCode('00:00:00:01')
        mo = TimeCode('00:00:00:03')
        gi = TimeCode('00:00:05:01')
        go = TimeCode('00:00:02:01')

        with self.assertRaises(RuntimeError):
            Edit(mi, mo, gi, go)

    def test_creation_with_attributes(self):
        mi = TimeCode('00:00:00:01')
        mo = TimeCode('00:00:00:03')
        gi = TimeCode('00:00:01:01')
        go = TimeCode('00:00:02:01')

        e = Edit(mi, mo, gi, go, name='stuff', number=1, blerg='wek')
        self.assertEquals(e.attributes(), {'name': 'stuff',
                                           'number': 1,
                                           'blerg': 'wek'})

    def test_mismatched_bases(self):
        mi = TimeCode('00:00:00:01', base=29.997)
        mo = TimeCode('00:00:00:03', base=20)
        gi = TimeCode('00:00:01:01', base=15)
        go = TimeCode('00:00:02:01', base=24)

        with self.assertRaises(RuntimeError):
            Edit(mi, mo, gi, go)


class TestEditMethods(unittest.TestCase):
    def setUp(self):
        self.mi = TimeCode('00:00:00:01')
        self.mo = TimeCode('00:00:00:03')
        self.gi = TimeCode('00:00:01:01')
        self.go = TimeCode('00:00:02:01')

        self.e = Edit(self.mi, self.mo, self.gi, self.go, name='stuff', number=1, blerg='wek')

    def test_get_media_in(self):
        self.assertEquals(self.e.mediaIn(), self.mi)

    def test_get_media_out(self):
        self.assertEquals(self.e.mediaOut(), self.mo)

    def test_get_global_in(self):
        self.assertEquals(self.e.globalIn(), self.gi)

    def test_get_global_in_with_ref_tc(self):
        ref_tc = TimeCode('00:00:02:00')
        self.assertEquals(self.e.globalIn(ref_tc).frames(), -23)

    def test_get_global_out(self):
        self.assertEquals(self.e.globalOut(), self.go)

    def test_get_global_out_with_ref_tc(self):
        ref_tc = TimeCode('00:00:02:00')
        self.assertEquals(self.e.globalOut(ref_tc).frames(), 1)

    def test_get_mediaInOut(self):
        self.assertEquals(self.e.mediaInOut(), (self.mi, self.mo))

    def test_get_globalInOut(self):
        self.assertEquals(self.e.globalInOut(), (self.gi, self.go))

    def test_get_globalInOut_with_ref_tc(self):
        ref_tc = TimeCode('00:00:02:00')
        g_in, g_out = self.e.globalInOut(ref_tc)
        self.assertEquals(g_in.frames(), -23)
        self.assertEquals(g_out.frames(), 1)

    def test_set_mediaIn(self):
        new_TC = TimeCode('00:00:00:05', base=24)
        self.e.setMediaIn(new_TC)
        self.assertEquals(self.e.mediaIn(), new_TC)

    def test_set_mediaIn_wrongBase(self):
        new_TC = TimeCode('00:00:00:05', base=10)
        with self.assertRaises(EditError):
            self.e.setMediaIn(new_TC)

    def test_set_mediaOut(self):
        new_TC = TimeCode('00:00:00:15', base=24)
        self.e.setMediaOut(new_TC)
        self.assertEquals(self.e.mediaOut(), new_TC)

    def test_set_mediaOut_wrongBase(self):
        new_TC = TimeCode('00:00:00:15', base=10)
        with self.assertRaises(EditError):
            self.e.setMediaOut(new_TC)

    def test_set_globalIn(self):
        new_TC = TimeCode('00:00:00:04', base=24)
        self.e.setGlobalIn(new_TC)
        self.assertEquals(self.e.globalIn(), new_TC)

    def test_set_globalIn_wrongBase(self):
        new_TC = TimeCode('00:00:00:04', base=10)
        with self.assertRaises(EditError):
            self.e.setGlobalIn(new_TC)

    def test_set_globalOut(self):
        new_TC = TimeCode('00:00:00:04', base=24)
        self.e.setGlobalOut(new_TC)
        self.assertEquals(self.e.globalOut(), new_TC)

    def test_set_globalOut_wrongBase(self):
        new_TC = TimeCode('00:00:00:04', base=10)
        with self.assertRaises(EditError):
            self.e.setGlobalOut(new_TC)

    def test_attribute_set_get(self):
        self.e.set('integer', 15)
        self.e.set('float', 1.0)
        self.e.set('string', 'this is')
        self.e.set('bool', False)

        self.assertEquals(self.e.get('integer'), 15)
        self.assertEquals(self.e.get('float'), 1.0)
        self.assertEquals(self.e.get('string'), 'this is')
        self.assertEquals(self.e.get('bool'), False)

    def test_attribute_get_default(self):
        assert self.e.get('get me some None') is None
        self.assertEquals(self.e.get('get me some defaults', 'default'), 'default')

    def test_repr(self):
        self.assertEquals(str(self.e), '< Edit: 00:00:01:01[00:00:00:01;00:00:00:03]00:00:02:01>')


if __name__ == '__main__':
    unittest.main()