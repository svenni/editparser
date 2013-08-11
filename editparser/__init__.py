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

'''
This module contains the parser function along with all the support classes.
'''

import sys


class ParserError(Exception):
    pass


class TimeCodeError(Exception):
    pass

class EditError(Exception):
    pass


def parse(edl_path, start_tc=None, format='cmx3600', base=25):
    '''
    Parses the given *edl_path* assuming the file is in the format *format*.
    '''

    try:
        __import__('%s.%s' % (__name__, format))
        parser = sys.modules['%s.%s' % (__name__, format)]
    except ImportError:
        raise ParserError('Invalid format')

    return parser.parse(edl_path, start_tc, base=base)


class TimeCode():
    def __init__(self, tc='00:00:00:00', frames=0, base=24):
        self._base = base

        if frames == 0 and tc != '00:00:00:00':
            self._frames = self.toFrames(tc)
        else:
            self._frames = frames

    @classmethod
    def from_msec(self, msec, base=24):
        millisec = msec % 1000
        seconds = int(msec / 1000)

        frames = (seconds * base) + int(base * millisec/1000)

        return TimeCode(frames=frames, base=base)

    def base(self):
        return self._base

    def tc(self):
        if self._frames < 0:
            prefix = '-'
            f = abs(self._frames)
        else:
            prefix = ''
            f = self._frames
        s = f // self._base
        f = f % self._base
        #print 's:', s, 'f:',f

        m = s // 60
        s = s % 60
        #print 'm:', m, 's:', s

        h = m // 60
        m = m % 60
        #print 'h', h, 'm:', m

        return '%s%02d:%02d:%02d:%02d' % (prefix, h, m, s, f)

    def frames(self):
        return self._frames

    def toFrames(self, tc):
        try:
            if tc[0] == '-':
                tc = tc[1:]
                multiplier = -1
            else:
                multiplier = 1

            h, m, s, f = tc.split(':')
        except (ValueError, IndexError):
            raise RuntimeError('Timecode of invalid format, \
                                expecting xx:xx:xx:xx, got %s' % tc)

        h = int(h)
        m = int(m)
        s = int(s)
        f = int(f)

        return multiplier * (f +
                             self._base * s +
                             self._base * 60 * m +
                             self._base*60*60*h)

    def __str__(self):
        return self.tc()

    def __repr__(self):
        return '<TimeCode:%s>' % self.__str__()

    def __add__(self, other):
        # adding Timecodes in different bases is possible but confusing, so we just error
        if self.base() != other.base():
            raise TimeCodeError('Cannot add two TimeCode objects with different bases!')

        newFrameLength = self._frames + other._frames
        return TimeCode(frames=newFrameLength, base=self.base())

    def __sub__(self, other):
        if self.base() != other.base():
            raise TimeCodeError('Cannot subtract two TimeCode objects with different bases!')

        newFrameLength = self._frames - other._frames
        return TimeCode(frames=newFrameLength, base=self.base())

    def __eq__(self, other):
        if self.base() != other.base():
            return False

        if self.frames() == other.frames():
            return True
        else:
            return False

    def __ne__(self, other):
        if self.frames() == other.frames():
            return False
        else:
            return True


class EDL():
    def __init__(self, title, path, startTimeCode='01:00:00:00', base=25):
        self._title = title
        self._edits = []
        self._edlPath = path
        self.startTC = TimeCode(startTimeCode, base=base)

    def appendEdit(self, edit):
        self._edits.append(edit)

    def insertEdit(self, index, edit):
        self._edits.insert(index, edit)

    def getAllEdits(self):
        return self._edits

    def getEdit(self, index):
        try:
            res = self._edits[index]
        except IndexError:
            res = None
        return res

    def title(self):
        return self._title

    def path(self):
        return self._edlPath

    def start_tc(self):
        return self.startTC


class Edit():
    def __init__(self, mediaIn, mediaOut, globalIn, globalOut, **kwargs):
        self._mediaIn = self.parse_input_tc(mediaIn)
        self._mediaOut = self.parse_input_tc(mediaOut)
        self._globalIn = self.parse_input_tc(globalIn)
        self._globalOut = self.parse_input_tc(globalOut)

        if self._globalIn.frames() > self._globalOut.frames():
            raise RuntimeError('Global In cannot be after Global Out!')

        if not (self._mediaIn.base() == self._mediaOut.base() ==
                self._globalIn.base() == self._globalOut.base()):
            raise RuntimeError('Input TimeCode objects do not have the same base.')

        self._attributes = kwargs

    def parse_input_tc(self, tc):
        if not isinstance(tc, TimeCode):
            # not timecode, check if input is string
            if isinstance(tc, basestring):
                try:
                    tc = TimeCode(tc)
                except RuntimeError:
                    raise RuntimeError('Invalid formatted TimeCode string "%s"' % tc)
            else:
                raise RuntimeError('Edit takes either TimeCode objects or TimeCode formatted strings as input!')
        return tc

    def mediaIn(self):
        return self._mediaIn

    def mediaOut(self):
        return self._mediaOut

    def globalIn(self, refTC=None):
        if refTC is None:
            refTC = TimeCode(frames=0, base=self._globalIn.base())
        return self._globalIn-refTC

    def globalOut(self, refTC=None):
        if refTC is None:
            refTC = TimeCode(frames=0, base=self._globalOut.base())
        return self._globalOut-refTC

    def mediaInOut(self):
        return (self._mediaIn, self._mediaOut)

    def globalInOut(self, refTC=None):
        if refTC is None:
            refTC = TimeCode(frames=0, base=self._globalIn.base())
        return (self.globalIn(refTC), self.globalOut(refTC))

    def setMediaIn(self, mediaIn):
        if mediaIn.base() != self._mediaIn.base():
            raise EditError('Wrong input base! Expected %s, got %s.' % (self._mediaIn.base(), mediaIn.base()))
        self._mediaIn = mediaIn

    def setMediaOut(self, mediaOut):
        if mediaOut.base() != self._mediaOut.base():
            raise EditError('Wrong input base! Expected %s, got %s.' % (self._mediaOut.base(), mediaOut.base()))
        self._mediaOut = mediaOut

    def setGlobalIn(self, globalIn):
        if globalIn.base() != self._globalIn.base():
            raise EditError('Wrong input base! Expected %s, got %s.' % (self._globalIn.base(), globalIn.base()))
        self._globalIn = globalIn

    def setGlobalOut(self, globalOut):
        if globalOut.base() != self._globalOut.base():
            raise EditError('Wrong input base! Expected %s, got %s.' % (self._globalOut.base(), globalOut.base()))
        self._globalOut = globalOut

    def get(self, attribute, default=None):
        return self._attributes.get(attribute, default)

    def set(self, attribute, value):
        self._attributes[attribute] = value

    def attributes(self):
        return self._attributes

    def __repr__(self):
        return '< Edit: %s[%s;%s]%s>' % (self._globalIn, self._mediaIn, self._mediaOut, self._globalOut)
