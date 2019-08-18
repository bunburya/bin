#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import re
from collections import OrderedDict

import notify2
notify2.init('Screen manager')

STATUS_RE = re.compile(r'(\w+) (dis)?connected (primary)? ?(\d+x\d+i?\+\d+\+\d+)?')

DEFAULT_PRIMARY = 'eDP1'

def notify(text):
    n = notify2.Notification('Screen manager', text)
    return n.show()

def get_xrandr():
    return subprocess.check_output('xrandr').decode().splitlines()

def set_xrandr(args):
    if args[0] != 'xrandr':
        args.insert(0, 'xrandr')
    print('calling {}'.format(args))
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

def get_connected(*display_names):
    all_displays = get_displays()
    display_names = display_names or all_displays.keys()
    return OrderedDict([(d, all_displays[d]) for d in display_names if all_displays[d]['connected']])

def get_active():
    all_displays = get_displays()
    return OrderedDict([(d, all_displays[d]) for d in all_displays if all_displays[d]['active']])

def decide_primary(displays, connected):
    if len(displays) == 1:
        # if only one display specified and it is connected, it is primary.
        d = displays[0]
        if d in connected:
            return d
    elif len(connected) == 1:
        # if only one display is connected and it is specified, it is primary.
        d = connected.copy().pop()
        if d in displays:
            return d
    elif DEFAULT_PRIMARY in displays and DEFAULT_PRIMARY in connected:
        # if a defined default is both connected and specified, it is primary.
        return DEFAULT_PRIMARY
    else:
        # specified display that is connected is primary
        for d in displays:
            if d in connected:
                return d
        else:
            # no primary
            return None

def set_active(*display_names):
    all_connected = get_connected()
    primary = decide_primary(display_names, all_connected)
    args = ['xrandr']
    if display_names:
        first_display = all_connected.get(display_names[0])
        if first_display:
            args = ['xrandr', '--output', display_names[0], '--auto']
            if display_names[0] == primary:
                args.append('--primary')
        else:
            notify('Display {} not connected.'.format(display_names[0]))
    for i, d in enumerate(display_names[1:]):
        try:
            current_display = all_connected.get(d)
            if current_display:
                args.append('--output')
                args.append(d)
                args.append('--auto')
                args.append('--right-of')
                args.append(display_names[i])
                if d == primary:
                    args.append('--primary')
            else:
                notify('Display {} not connected.'.format(d))
        except KeyError:
            notify('Display {} not found.'.format(d))
    
    # Turn everything else off
    for d in all_connected.keys():
        print(d)
        print(display_names)
        if d not in display_names:
            args.append('--output')
            args.append(d)
            args.append('--off')
    set_xrandr(args)

if __name__ == '__main__':
    # if called from shell, activate all connected screens
    set_active(*get_connected())
