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

    # check if we there is a TITLE specified
    search = re.search(r'TITLE:\s+(.*)', edl_lines[0])
    if not search:
        edl_name = 'edl'
    else:
        edl_name = search.groups(0)[0].strip()

    #if start_tc is not None and not isinstance(start_tc, TimeCode):
    #    raise ParserError('Input start_tc is not a TimeCode instance!')

    if start_tc:
        the_edl = EDL(edl_name, edl_path, start_tc, base=base)
    else:
        the_edl = EDL(edl_name, edl_path, base=base)

    event_expr = re.compile(r'(\d{3}).*')
    edit_search_exp = re.compile(r'\d{3}.*[A-Z]\s(.*)')
    edit_name_exp = re.compile(r'\*\sFROM\sCLIP\sNAME:\s(.*)')
    current_edit = None

    for i in range(len(edl_lines)):
        line = edl_lines[i].strip()
        if re.match(event_expr, line):
            parsed_line = parse_event_line(line, base)
            mi = parsed_line.pop('media_in')
            mo = parsed_line.pop('media_out')
            gi = parsed_line.pop('global_in')
            go = parsed_line.pop('global_out')
            current_edit = Edit(mi, mo, gi, go, **parsed_line)
            the_edl.appendEdit(current_edit)
        else:
            line_info = parse_info_line(line)
            for k, v in line_info.items():
                if current_edit is not None:
                    current_edit.set(k, v)

    return the_edl

def parse_event_line(line, base=24):
    expr = r'(?P<number>\d{3})\s*(?P<tape>[A-Z_0-9]*)\s(?P<channel>[VA]+)\s*(?P<transition>\w)\s*(?P<duration>\d{3})?\s(?P<mi>\d\d:\d\d:\d\d:\d\d)\s(?P<mo>\d\d:\d\d:\d\d:\d\d)\s(?P<gi>\d\d:\d\d:\d\d:\d\d)\s(?P<go>\d\d:\d\d:\d\d:\d\d)'
    search = re.search(expr, line)
    if search is not None:
        return {
        'number': int(search.group('number')),
        'tape': search.group('tape'),
        'channels': list(search.group('channel')),
        'transition': search.group('transition'),
        'duration': search.group('duration') or 0,
        'media_in': TimeCode(search.group('mi'), base=base),
        'media_out': TimeCode(search.group('mo'), base=base),
        'global_in': TimeCode(search.group('gi'), base=base),
        'global_out': TimeCode(search.group('go'), base=base),
        }
    else:
        raise ParserError('Invalid event line!')
    

def parse_info_line(line):
    info = {}

    # first try splitting the line on ':'
    line_parts = line.split(':')
    if len(line_parts) > 1:
        # we have a key: value situation
        value = line_parts[1].strip()
    else:
        # just key
        value = True

    key = line_parts[0].replace('*', '').strip().replace(' ','_').lower()
    info[key] = value

    return info
