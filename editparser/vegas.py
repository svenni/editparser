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

from . import EDL, TimeCode, Edit, ParserError


def parse(edl_path, start_tc=None, base=25):
    
    if not os.path.exists(edl_path):
        raise IOError('Path does not exist: %s' % edl_path)

    edl_file = open(edl_path, 'rt')
    edl_lines = edl_file.readlines()
    edl_file.close()

    if edl_lines[0].startswith('"ID"'):
        del edl_lines[0]

    edl_name = os.path.basename(edl_path)

    if start_tc:
        the_edl = EDL(edl_name, edl_path, TimeCode(start_tc), base=base)
    else:
        the_edl = EDL(edl_name, edl_path, base=base)

    for line in edl_lines:
        try:
            vLine = VegasEDLLine(line)
        except ParserError, err:
            print 'ERROR:', err
            continue

        try:
            edit_number = vLine.ID
            edit_name = os.path.basename(vLine.FileName)
        except AttributeError, err:
            print 'ERROR:', err
            continue

        global_in_tc = TimeCode.from_msec(vLine.StartTime, base=base)
        global_length_tc = TimeCode.from_msec(vLine.Length, base=base)
        global_out_tc = global_in_tc + global_length_tc

        media_in_tc = TimeCode.from_msec(vLine.StreamStart, base=base)
        media_length_tc = TimeCode.from_msec(vLine.StreamLength, base=base)
        media_out_tc = media_in_tc + media_length_tc

        current_edit = Edit(media_in_tc, media_out_tc, global_in_tc, global_out_tc, **vLine._dict)
        the_edl.appendEdit(current_edit)

    return the_edl




    '''


    edit_number_exp = re.compile(r'(\d{3})')
    edit_search_exp = re.compile(r'\d{3}.*[A-Z]\s(.*)')
    edit_name_exp = re.compile(r'\*\sFROM\sCLIP\sNAME:\s(.*)')

    for i in range(2, len(edl_lines), 2):
        tc_line = edl_lines[i]
        name_line = edl_lines[i+1]
        edit_search = re.search(edit_search_exp, tc_line)
        if edit_search:
            edit_tc = edit_search.groups(0)[0].strip()
        else:
            continue

        edit_number_search = re.search(edit_number_exp, tc_line)
        if edit_number_search:
            edit_number = int(edit_number_search.groups(0)[0])
        else:
            edit_number = 1

        edit_name_search = re.search(edit_name_exp, name_line)
        if edit_name_search:
            edit_name = edit_name_search.groups(0)[0].strip()
        else:
            edit_name = 'edit'

        tc_parts = edit_tc.split(' ')

        media_in_out = (TimeCode(tc_parts[0]), TimeCode(tc_parts[1]))
        global_in_out = (TimeCode(tc_parts[2]), TimeCode(tc_parts[3]))

        current_edit = Edit(edit_number, edit_name, media_in_out, global_in_out)
        the_edl.appendEdit(current_edit)

    return the_edl
    '''


class VegasEDLLine(object):
    def __init__(self, line):
        self._fields = ['ID',
                        'Track',
                        'StartTime',
                        'Length',
                        'PlayRate',
                        'Locked',
                        'Normalized',
                        'StretchMethod',
                        'Looped',
                        'OnRuler',
                        'MediaType',
                        'FileName',
                        'Stream',
                        'StreamStart',
                        'StreamLength',
                        'FadeTimeIn',
                        'FadeTimeOut',
                        'SustainGain',
                        'CurveIn',
                        'GainIn',
                        'CurveOut',
                        'GainOut',
                        'Layer',
                        'Color',
                        'CurveInR',
                        'CurveOutR',
                        'PlayPitch',
                        'LockPitch',
                        'FirstChannel',
                        'Channels']
        self._dict = {}

        line_parts = line.split(';')

        if len(line_parts) != len(self._fields):
            raise ParserError('Mismatched line/field count!')

        for field, line_part in zip(self._fields, line_parts):
            line_part = line_part.strip()
            value = ''

            # check if it is a bool value
            if line_part == 'FALSE':
                value = False

            elif line_part == 'TRUE':
                value = True

            else:
                try:
                    int_value = int(line_part)
                    value = int_value
                except ValueError:
                    try:
                        value = float(line_part)
                    except ValueError:
                        value = line_part

            if isinstance(value, str):
                value = value.replace('"', '')

            #print '%s -> %s (%s) type:%s' % (field, value, line_part, type(value))

            self._dict[field] = value

    def __getattr__(self, name):
        if name not in self._dict.keys():
            raise AttributeError('VegasEDLLine does not have the field \'%s\'' % name)

        return self._dict[name]



