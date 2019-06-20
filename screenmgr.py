#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import re
from collections import OrderedDict

import notify2
notify2.init('Screen manager')

STATUS_RE = re.compile(r'(\w+) (dis)?connected (primary)? ?(\d+x\d+i?\+\d+\+\d+)?')

def notify(text):
    n = notify2.Notification('Screen manager', text)
    return n.show()

def get_xrandr():
    return subprocess.check_output('xrandr').decode().splitlines()

def set_xrandr(args):
    if args[0] != 'xrandr':
        args.insert(0, 'xrandr')
    subprocess.call(args)

def get_displays(xrandr_output=None):
    if xrandr_output is None:
        xrandr_output = get_xrandr()
    displays = OrderedDict()
    for line in xrandr_output:
        m = STATUS_RE.match(line)
        if m is not None:
            g = m.groups()
            displays[g[0]] = {
                    'connected': g[1] is None,
                    'primary': g[2] == 'primary',
                    'active': g[3] is not None
                    }
    return displays

def get_connected():
    all_displays = get_displays()
    return OrderedDict([(d, all_displays[d]) for d in all_displays if all_displays[d]['connected']])

def get_active():
    all_displays = get_displays()
    return OrderedDict([(d, all_displays[d]) for d in all_displays if all_displays[d]['active']])

def set_active(*displays):
    all_displays = get_displays()
    if displays:
        if all_displays[displays[0]]['connected']:
            args = ['xrandr', '--output', displays[0], '--auto']
        else:
            notify('Display {} not connected.'.format(displays[0]))
    else:
        args = []
    for i, d in enumerate(displays[1:]):
        try:
            if all_displays[d]['connected']:
                args.append('--output')
                args.append(d)
                args.append('--auto')
                args.append('--right-of')
                args.append(displays[i])
            else:
                notify('Display {} not connected.'.format(d))
        except KeyError:
            notify('Display {} not found.'.format(d))
    for d in all_displays:
        if d not in displays:
            args.append('--output')
            args.append(d)
            args.append('--off')
    set_xrandr(args)

if __name__ == '__main__':
    # if called from shell, activate all connected screens
    set_active(*get_connected())
