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


import os
import re
import sys

class ParserError(Exception):
    pass

def parse(edl_path, start_tc=None, format='cmx3600'):
    try:
        __import__('editparser.%s' % format)
        parser = sys.modules['editparser.%s' % format]
    except ImportError:
        raise ParserError('Invalid format')
    
    return parser.parse(edl_path, start_tc)

			
class TimeCode():
    def __init__(self, tc='00:00:00:00', frames=0, base=24):
        self._base = base
        
        if frames == 0 and tc !='00:00:00:00':
            self._frames = self.toFrames(tc)
        else:
            self._frames = frames		
        
    
    def tc(self):
        if self._frames<0:
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
        
        return '%s%02d:%02d:%02d:%02d' % (prefix, h,m,s,f)
    
    def frames(self):
        return self._frames
    
    def toFrames(self, tc):
        try:
            if tc[0] == '-':
                tc = tc[1:]
                multiplier = -1
            else:
                multiplier = 1
             
            h,m,s,f = tc.split(':')
        except (ValueError, IndexError):
            raise RuntimeError('Timecode of invalid format, \
			                    expecting xx:xx:xx:xx, got %s' % tc)
		
        h=int(h)
        m=int(m)
        s=int(s)
        f=int(f)

        return multiplier * (   f + 
		                        self._base * s + 
		                        self._base * 60 * m + 
		                        self._base*60*60*h )
    		
    def __str__(self):
        return self.tc()
    def __repr__(self):
        return self.__str__()
        
    def __add__(self, other):
        newFrameLength = self._frames + other._frames
        return TimeCode(frames=newFrameLength)
        
    def __sub__(self, other):
        newFrameLength = self._frames - other._frames
        return TimeCode(frames=newFrameLength)

class EDL():
	def __init__(self, title, path, startTimeCode=TimeCode('01:00:00:00')):
		self._title = title
		self._edits = []
		self._edlPath = path
		self.startTC = startTimeCode
		
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
		
class Edit():
	def __init__(self, number, name, mediaInOut, globalInOut ):
		self._number = number
		self._name = name
		
		self.setMediaInOut(mediaInOut)
		self.setGlobalInOut(globalInOut)
		
	def name(self):
		return self._name
	def number(self):
		return self._number
	
	def setNumber(self, number):
		self._number = number
	def setName(self, name):
		self._name = name
	
	def mediaIn(self):
		return self._mediaIn
	def mediaOut(self):
		return self._mediaOut
	def globalIn(self, refTC=TimeCode(frames=0)):
		return self._globalIn-refTC
	def globalOut(self, refTC=TimeCode(frames=0)):
		return self._globalOut-refTC
		
	def mediaInOut(self):
		return (self._mediaIn, self._mediaOut)
	def globalInOut(self, refTC=TimeCode(frames=0)):
		return (self._globalIn-refTC, self._globalOut-refTC)
		
		
	def setMediaInOut(self, mediaInOut):
		self._mediaIn = mediaInOut[0]
		self._mediaOut = mediaInOut[1]
	def setGlobalInOut(self, globalInOut):
		self._globalIn = globalInOut[0]
		self._globalOut = globalInOut[1]
	
		
	def setMediaIn(self, mediaIn):
		self._mediaIn = mediaIn
	def setMediaOut(self, mediaOut):
		self._mediaOut = mediaOut
	def setGlobalIn(self, globalIn):
		self._globalIn = globalIn
	def setGlobalOut(self, globalOut):
		self._globalOut = globalOut
	
	
	def __repr__(self):
		return str(self._number).rjust(3,'0')+ ' - ' + str(self._name) + ' - ' + str(self._mediaIn)

		
