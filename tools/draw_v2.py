#!/usr/bin/env python3
"""Draws the "Redrawn" (v2) art set for the dashboard as hand-built SVGs.

Run:  python3 tools/draw_v2.py
Writes to assets/v2/ :
  bg-{freezing,chilly,mild,warm,heatwave}.svg      1200x400 scenes
  char-{freezing,chilly,mild,warm,heatwave}.svg    500x500 character sprites
  overlay-{rain,snow,hail,tornado}.svg             500x500 floating weather
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'v2')
INK = '#1a1a1a'
CREAM = '#f4eedd'


# ----------------------------------------------------------------- helpers
def svg(w, h, body, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" stroke-linejoin="round" stroke-linecap="round">'
            f'<defs>{defs}</defs>{body}</svg>\n')


def blob(circles, fill, sw=8, stroke=INK, highlight=None):
    """Union of circles with one shared outline (stroke pass, then fill pass)."""
    s = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{stroke}" '
                f'stroke="{stroke}" stroke-width="{sw}"/>' for x, y, r in circles)
    s += ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"/>'
                 for x, y, r in circles)
    if highlight:
        s += ''.join(f'<circle cx="{x - r * .25:.1f}" cy="{y - r * .25:.1f}" r="{r * .55:.1f}" '
                     f'fill="{highlight}" opacity=".55"/>' for x, y, r in circles[:3])
    return s


def pts(points):
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)


def tube(points, color, w, ow=8):
    """Rubber-hose limb: thick outlined polyline."""
    p = pts(points)
    return (f'<polyline points="{p}" fill="none" stroke="{INK}" stroke-width="{w + ow}"/>'
            f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}"/>')


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def pie_eye(x, y, rx, ry):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{INK}"/>'
            f'<polygon points="{pts([(x, y - .1 * ry), (x - .6 * rx, y - .7 * ry), (x + .1 * rx, y - .85 * ry)])}" fill="#fff"/>')


def glove(hand, elbow, r=17, wave=False):
    hx, hy = hand
    dx, dy = hx - elbow[0], hy - elbow[1]
    d = math.hypot(dx, dy) or 1
    cx, cy = hx - dx / d * r * .9, hy - dy / d * r * .9
    s = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * .7:.1f}" fill="#fff" stroke="{INK}" stroke-width="4"/>'
    s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="4"/>'
    # finger creases
    for k in (-1, 0, 1):
        ang = math.atan2(dy, dx) + k * .45
        x1, y1 = hx + math.cos(ang) * r * .2, hy + math.sin(ang) * r * .2
        x2, y2 = hx + math.cos(ang) * r * .85, hy + math.sin(ang) * r * .85
        s += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="2.5"/>'
    if wave:
        for i, off in enumerate((-30, -18)):
            s += (f'<path d="M{hx + 24 + i * 8},{hy + off} q8,10 0,22" fill="none" '
                  f'stroke="{INK}" stroke-width="3"/>')
    return s


def drop(x, y, s=1.0, fill='#8cc4e8'):
    return (f'<path d="M{x},{y} q{7 * s},{12 * s} {7 * s},{17 * s} a{7 * s},{7 * s} 0 0 1 {-14 * s},0 '
            f'q0,{-5 * s} {7 * s},{-17 * s}z" fill="{fill}" stroke="{INK}" stroke-width="3"/>')


# ----------------------------------------------------------------- characters
OUTFITS = {
    'freezing': dict(
        man=dict(top='parka', top_c='#2f4a6b', sleeves='long', legs='pants', legs_c='#33302c', shoes='#5a3a22',
                 hat='beanie', hat_c='#b8322a', scarf='#d9a43a'),
        woman=dict(top='parka', top_c='#7b2d3b', sleeves='long', legs='pants', legs_c='#2e3b55', shoes='#4a2e1e',
                   hat='beanie', hat_c='#e6d7b8', scarf='#2f6b5a'),
        extra='breath'),
    'chilly': dict(
        man=dict(top='hoodie', top_c='#2b2b2b', inner='#9a9a9a', sleeves='long', legs='pants', legs_c='#3b5a80',
                 shoes='#c9a77a'),
        woman=dict(top='jacket', top_c='#5a7fa8', inner='#f0ece0', sleeves='long', legs='pants', legs_c='#8c8478',
                   shoes='#6f9a86'),
        extra='coffee'),
    'mild': dict(
        man=dict(top='flannel', top_c='#8b3a3a', sleeves='long', legs='pants', legs_c='#bfa57a', shoes='#5a3a22'),
        woman=dict(top='jacket', top_c='#5e8a4a', inner='#f4eedd', sleeves='long', legs='pants', legs_c='#3b5a80',
                   shoes='#c9a77a'),
        extra=None),
    'warm': dict(
        man=dict(top='tee', top_c='#f7f5ef', sleeves='short', legs='shorts', legs_c='#4d6f99', shoes='#c9a77a'),
        woman=dict(top='blouse', top_c='#eef1ea', sleeves='short', legs='shorts', legs_c='#efe4cc', shoes='#6f9a86'),
        extra=None),
    'heatwave': dict(
        man=dict(top='tank', top_c='#f2c94c', sleeves='none', legs='shorts', legs_c='#c0392b', shoes='#f0f0f0'),
        woman=dict(top='tank', top_c='#e07a5f', sleeves='none', legs='shorts', legs_c='#f4eedd', shoes='#c9a77a',
                   hat='sunhat', hat_c='#e8d29a'),
        extra='sweat'),
}

MAN_SKIN, BEARD = '#e3a77c', '#4a2c1a'
WOMAN_SKIN, HAIR = '#8d5a3b', '#a8362a'


def torso(path, o, cx, neck_y):
    c = o['top_c']
    fill = 'url(#plaid)' if o['top'] == 'flannel' else c
    s = f'<path d="{path}" fill="{fill}" stroke="{INK}" stroke-width="5"/>'
    t = o['top']
    if t in ('tee', 'blouse', 'flannel'):
        s += f'<path d="M{cx - 16},{neck_y} Q{cx},{neck_y + 18} {cx + 16},{neck_y}" fill="none" stroke="{INK}" stroke-width="4"/>'
    if t == 'blouse':
        s += (f'<path d="M{cx - 18},{neck_y - 2} L{cx},{neck_y + 16} L{cx - 4},{neck_y - 4}Z" fill="#fff" stroke="{INK}" stroke-width="3"/>'
              f'<path d="M{cx + 18},{neck_y - 2} L{cx},{neck_y + 16} L{cx + 4},{neck_y - 4}Z" fill="#fff" stroke="{INK}" stroke-width="3"/>')
        s += ''.join(f'<circle cx="{cx}" cy="{neck_y + 30 + i * 18}" r="2.5" fill="{INK}"/>' for i in range(4))
    if t == 'tank':
        s += f'<path d="M{cx - 20},{neck_y - 4} Q{cx},{neck_y + 26} {cx + 20},{neck_y - 4}" fill="{o.get("skin")}" stroke="{INK}" stroke-width="4"/>'
    if t in ('hoodie', 'jacket'):
        s += (f'<path d="M{cx - 14},{neck_y} L{cx - 8},{neck_y + 100} L{cx + 8},{neck_y + 100} L{cx + 14},{neck_y}Z" '
              f'fill="{o["inner"]}" stroke="{INK}" stroke-width="3.5"/>')
    if t == 'hoodie':
        s += (f'<path d="M{cx - 30},{neck_y + 62} h60 l6,30 h-72z" fill="none" stroke="{INK}" stroke-width="3"/>'
              f'<line x1="{cx - 5}" y1="{neck_y + 4}" x2="{cx - 7}" y2="{neck_y + 34}" stroke="#ddd" stroke-width="3"/>'
              f'<line x1="{cx + 5}" y1="{neck_y + 4}" x2="{cx + 7}" y2="{neck_y + 34}" stroke="#ddd" stroke-width="3"/>')
    if t == 'jacket':
        s += ''.join(f'<circle cx="{cx + 16}" cy="{neck_y + 25 + i * 22}" r="3" fill="{INK}"/>' for i in range(3))
        s += f'<path d="M{cx - 40},{neck_y + 40} h18 v14 h-18z" fill="none" stroke="{INK}" stroke-width="3"/>'
    if t == 'parka':
        for i in range(1, 4):
            s += f'<path d="M{cx - 44},{neck_y + i * 28} Q{cx},{neck_y + i * 28 + 8} {cx + 44},{neck_y + i * 28}" fill="none" stroke="{INK}" stroke-width="3" opacity=".6"/>'
        s += f'<line x1="{cx}" y1="{neck_y}" x2="{cx}" y2="{neck_y + 108}" stroke="{INK}" stroke-width="3"/>'
    return s


def legs(hips, knees, feet, o, skin):
    s = ''
    for hip, knee, foot in zip(hips, knees, feet):
        if o['legs'] == 'pants':
            s += tube([hip, knee, foot], o['legs_c'], 30)
        else:
            s += tube([hip, knee, foot], skin, 20)
            s += tube([hip, lerp(hip, knee, .7)], o['legs_c'], 34)
        fx, fy = foot
        s += f'<ellipse cx="{fx + 12}" cy="{fy + 4}" rx="27" ry="13" fill="{o["shoes"]}" stroke="{INK}" stroke-width="5"/>'
        s += f'<path d="M{fx - 6},{fy + 12} h38" stroke="{INK}" stroke-width="3"/>'
    return s


def arm(shoulder, elbow, hand, o, skin, wave=False):
    s = ''
    if o['sleeves'] == 'long':
        s += tube([shoulder, elbow, hand], o['top_c'] if o['top'] != 'flannel' else '#8b3a3a', 24)
    else:
        s += tube([shoulder, elbow, hand], skin, 17)
        if o['sleeves'] == 'short':
            s += tube([shoulder, lerp(shoulder, elbow, .55)], o['top_c'], 28)
    s += glove(hand, elbow, wave=wave)
    return s


def hip_block(path, o):
    return f'<path d="{path}" fill="{o["legs_c"]}" stroke="{INK}" stroke-width="5"/>'


def scarf(cx, y, w, color):
    return (f'<path d="M{cx - w},{y} Q{cx},{y + 14} {cx + w},{y} l2,16 Q{cx},{y + 30} {cx - w - 2},{y + 16}z" fill="{color}" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M{cx + w - 14},{y + 18} l6,58 l18,-4 l-6,-56z" fill="{color}" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M{cx + w - 8},{y + 64} l16,-3" stroke="{INK}" stroke-width="3"/>')


def beanie(cx, top, r, color):
    return (f'<path d="M{cx - r - 4},{top + r * .95} Q{cx - r},{top - 4} {cx},{top - 6} Q{cx + r},{top - 4} {cx + r + 4},{top + r * .95}Z" '
            f'fill="{color}" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="{cx - r - 7}" y="{top + r * .72}" width="{2 * r + 14}" height="{r * .38}" rx="8" fill="{color}" stroke="{INK}" stroke-width="5"/>'
            + ''.join(f'<line x1="{cx - r + i * r / 3:.0f}" y1="{top + r * .76:.0f}" x2="{cx - r + i * r / 3:.0f}" y2="{top + r * 1.06:.0f}" stroke="{INK}" stroke-width="2.5" opacity=".5"/>'
                      for i in range(1, 6))
            + f'<circle cx="{cx}" cy="{top - 10}" r="14" fill="#fff" stroke="{INK}" stroke-width="5"/>')


def man_head(o):
    cx, cy, r = 170, 148, 52
    s = f'<rect x="156" y="186" width="28" height="32" fill="{MAN_SKIN}" stroke="{INK}" stroke-width="5"/>'
    s += f'<circle cx="119" cy="152" r="11" fill="{MAN_SKIN}" stroke="{INK}" stroke-width="5"/>'
    s += f'<circle cx="221" cy="152" r="11" fill="{MAN_SKIN}" stroke="{INK}" stroke-width="5"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{MAN_SKIN}" stroke="{INK}" stroke-width="5"/>'
    s += f'<ellipse cx="148" cy="112" rx="15" ry="8" fill="#fff" opacity=".55" transform="rotate(-30 148 112)"/>'
    # beard + mustache + grin
    s += f'<path d="M120,150 Q116,222 170,226 Q224,222 220,150 Q206,180 170,178 Q134,180 120,150Z" fill="{BEARD}" stroke="{INK}" stroke-width="5"/>'
    s += f'<path d="M152,184 Q170,202 188,184Z" fill="#fff" stroke="{INK}" stroke-width="3.5"/>'
    s += f'<path d="M142,176 Q170,160 198,176 Q170,184 142,176Z" fill="{BEARD}" stroke="{INK}" stroke-width="3.5"/>'
    s += f'<path d="M165,160 q5,6 10,0" fill="none" stroke="{INK}" stroke-width="3.5"/>'
    # brows + sunglasses
    s += f'<path d="M138,122 q14,-8 28,0 M174,122 q14,-8 28,0" fill="none" stroke="{BEARD}" stroke-width="6"/>'
    s += (f'<rect x="135" y="128" width="31" height="22" rx="9" fill="{INK}"/>'
          f'<rect x="174" y="128" width="31" height="22" rx="9" fill="{INK}"/>'
          f'<path d="M166,134 h8 M135,134 h-15 M205,134 h15" stroke="{INK}" stroke-width="4"/>'
          f'<path d="M141,134 l8,-3 M180,134 l8,-3" stroke="#fff" stroke-width="3" opacity=".8"/>')
    if o.get('hat') == 'beanie':
        s += beanie(cx, cy - r + 2, r, o['hat_c'])
    return s


def woman_hair_back():
    cs = [(286, 128, 24), (300, 100, 24), (330, 90, 26), (360, 100, 24), (376, 128, 24), (382, 158, 22),
          (386, 188, 22), (382, 218, 20), (282, 160, 22), (278, 190, 22), (283, 218, 20), (330, 112, 30)]
    return blob(cs, HAIR, sw=9)


def woman_head(o):
    cx, cy, r = 330, 152, 46
    s = f'<rect x="318" y="190" width="24" height="34" fill="{WOMAN_SKIN}" stroke="{INK}" stroke-width="5"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{WOMAN_SKIN}" stroke="{INK}" stroke-width="5"/>'
    s += blob([(300, 118, 15), (318, 108, 16), (338, 106, 16), (356, 112, 15), (368, 126, 12), (293, 132, 11)], HAIR, sw=7)
    s += pie_eye(316, 153, 5, 8) + pie_eye(344, 153, 5, 8)
    s += (f'<circle cx="316" cy="152" r="14" fill="#fff" fill-opacity=".12" stroke="#6b3a1f" stroke-width="3.5"/>'
          f'<circle cx="344" cy="152" r="14" fill="#fff" fill-opacity=".12" stroke="#6b3a1f" stroke-width="3.5"/>'
          f'<path d="M330,151 h0" stroke="#6b3a1f" stroke-width="4"/>'
          f'<path d="M302,152 h-12 M358,152 h12" stroke="#6b3a1f" stroke-width="3"/>')
    s += f'<path d="M327,166 q3,4 6,0" fill="none" stroke="{INK}" stroke-width="3"/>'
    s += f'<path d="M313,175 Q330,198 347,175Z" fill="#7a1f1f" stroke="{INK}" stroke-width="4"/>'
    s += f'<path d="M316,177 Q330,183 344,177 L342,181 Q330,186 318,181Z" fill="#fff"/>'
    s += f'<ellipse cx="304" cy="170" rx="7" ry="4" fill="#e0707a" opacity=".5"/><ellipse cx="356" cy="170" rx="7" ry="4" fill="#e0707a" opacity=".5"/>'
    hat = o.get('hat')
    if hat == 'beanie':
        s += beanie(cx, cy - r - 4, r + 6, o['hat_c'])
    elif hat == 'sunhat':
        c = o['hat_c']
        s += (f'<ellipse cx="{cx}" cy="116" rx="82" ry="18" fill="{c}" stroke="{INK}" stroke-width="5"/>'
              f'<path d="M290,116 Q292,70 330,68 Q368,70 370,116Z" fill="{c}" stroke="{INK}" stroke-width="5"/>'
              f'<path d="M292,104 Q330,114 368,104 L369,114 Q330,124 291,114Z" fill="#c0392b" stroke="{INK}" stroke-width="3"/>'
              f'<circle cx="360" cy="106" r="7" fill="#f2c94c" stroke="{INK}" stroke-width="3"/>')
    return s


def extras(kind):
    if kind == 'breath':
        return ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="3" opacity=".9"/>'
                       for x, y, r in [(236, 196, 9), (252, 186, 12), (272, 178, 8), (398, 182, 8), (414, 170, 11), (432, 162, 7)])
    if kind == 'sweat':
        return drop(110, 96, 1.1) + drop(232, 116, .9) + drop(282, 84, 1.0) + drop(392, 140, .8)
    return ''


def held_item(kind, hand):
    hx, hy = hand
    if kind == 'coffee':
        return (f'<path d="M{hx - 14},{hy - 40} h28 l-4,38 h-20z" fill="#f4eedd" stroke="{INK}" stroke-width="4"/>'
                f'<rect x="{hx - 15}" y="{hy - 26}" width="30" height="11" fill="#8a5a3c" stroke="{INK}" stroke-width="3"/>'
                f'<path d="M{hx - 16},{hy - 44} h32 v5 h-32z" fill="#6b4a32" stroke="{INK}" stroke-width="3"/>'
                f'<path d="M{hx - 4},{hy - 52} q-6,-8 0,-14 M{hx + 6},{hy - 52} q-6,-8 0,-14" fill="none" stroke="{INK}" stroke-width="2.5" opacity=".6"/>')
    if kind == 'icecream':
        return (f'<path d="M{hx - 14},{hy - 12} L{hx},{hy + 26} L{hx + 14},{hy - 12}Z" fill="#d9a05b" stroke="{INK}" stroke-width="4"/>'
                f'<path d="M{hx - 8},{hy - 4} l12,14 M{hx + 8},{hy - 4} l-12,14" stroke="{INK}" stroke-width="2"/>'
                + blob([(hx - 8, hy - 22, 12), (hx + 8, hy - 22, 12), (hx, hy - 36, 13)], '#f4b6c2', sw=7)
                + drop(hx + 12, hy - 10, .6, '#f4b6c2'))
    return ''


def character(temp):
    o = OUTFITS[temp]
    m, w = dict(o['man'], skin=MAN_SKIN), dict(o['woman'], skin=WOMAN_SKIN)
    body = '<ellipse cx="255" cy="462" rx="195" ry="18" fill="#000" opacity=".22"/>'
    # --- woman (behind)
    body += woman_hair_back()
    body += legs([(314, 322), (350, 322)], [(302, 384), (372, 380)], [(288, 444), (390, 436)], w, WOMAN_SKIN)
    body += hip_block('M288,298 L372,298 L378,334 Q330,342 282,334Z', w)
    body += arm((368, 236), (414, 222), (424, 164), w, WOMAN_SKIN, wave=True)
    body += torso('M292,226 Q330,214 368,226 L374,312 Q330,322 286,312Z', w, 330, 224)
    body += woman_head(w)
    if w['top'] == 'parka':
        body += scarf(330, 208, 26, w['scarf'])
    # --- man (front)
    body += legs([(148, 336), (192, 336)], [(132, 392), (210, 390)], [(116, 448), (220, 442)], m, MAN_SKIN)
    body += hip_block('M120,314 L220,314 L226,350 Q170,358 114,350Z', m)
    body += arm((130, 230), (106, 284), (110, 336), m, MAN_SKIN)
    body += torso('M126,214 Q170,200 214,214 L222,332 Q170,344 118,332Z', m, 170, 214)
    body += man_head(m)
    if m['top'] == 'parka':
        body += scarf(170, 204, 32, m['scarf'])
    # --- linked arms in front
    body += arm((210, 232), (242, 286), (276, 270), m, MAN_SKIN)
    body += arm((294, 238), (266, 290), (232, 282), w, WOMAN_SKIN)
    # --- props
    if o['extra'] == 'coffee':
        body += held_item('coffee', (110, 336))
    if temp == 'heatwave':
        body += held_item('icecream', (110, 330))
    body += extras(o['extra'])
    defs = ('<pattern id="plaid" width="24" height="24" patternUnits="userSpaceOnUse">'
            '<rect width="24" height="24" fill="#8b3a3a"/>'
            '<rect width="24" height="8" y="8" fill="#5e2424" opacity=".7"/>'
            '<rect width="8" height="24" x="8" fill="#5e2424" opacity=".7"/>'
            '<path d="M0,20 H24 M20,0 V24" stroke="#e0c080" stroke-width="1.5"/></pattern>')
    return svg(500, 500, body, defs)


# ----------------------------------------------------------------- backgrounds
SEASONS = {
    'freezing': dict(sky=('#b9c6d0', '#eef2f4'), hills='#c4ced6', ground='#f3f5f6', path='#dfe5e8', river='#c7dbe6',
                     tree='bare', crown=None, sun=('#f1e6b8', 46, 'shiver'), clouds=5, frozen=True),
    'chilly': dict(sky=('#a3b4c0', '#e2e4de'), hills='#8e9b85', ground='#8e9a66', path='#cbb894', river='#7f9fb3',
                   tree='autumn', crown=('#c2692b', '#d9a03a', '#8c4a2a'), sun=('#f3d88a', 52, 'calm'), clouds=4),
    'mild': dict(sky=('#97c3db', '#e8f1ee'), hills='#86a879', ground='#7aa956', path='#d8c49a', river='#6fa3c4',
                 tree='full', crown=('#5f9a45', '#88b551', '#4d7f3a'), sun=('#f6d55c', 58, 'smile'), clouds=3),
    'warm': dict(sky=('#78b9df', '#f4f0d6'), hills='#7aa86a', ground='#66a64a', path='#e2cd9c', river='#5c9ccc',
                 tree='full', crown=('#3f8a3a', '#6db04a', '#2f6e2e'), sun=('#f8cf3f', 66, 'grin'), clouds=3),
    'heatwave': dict(sky=('#eeb25a', '#fbe8b2'), hills='#c9a96a', ground='#c8b05e', path='#ead3a0', river='#7aa9b8',
                     tree='full', crown=('#9fa23a', '#c4b84a', '#7f842e'), sun=('#ffcf3a', 92, 'cool'), clouds=1, heat=True),
}


def bg_cloud(x, y, s, fill='#fbfaf5', face=True):
    cs = [(x, y, 26 * s), (x + 28 * s, y - 14 * s, 30 * s), (x + 60 * s, y, 24 * s), (x + 30 * s, y + 8 * s, 24 * s),
          (x - 22 * s, y + 8 * s, 16 * s), (x + 80 * s, y + 8 * s, 15 * s)]
    out = blob(cs, fill, sw=5)
    if face:
        fx, fy = x + 30 * s, y - 2 * s
        out += (f'<ellipse cx="{fx - 9 * s:.1f}" cy="{fy:.1f}" rx="{3 * s:.1f}" ry="{5 * s:.1f}" fill="{INK}"/>'
                f'<ellipse cx="{fx + 9 * s:.1f}" cy="{fy:.1f}" rx="{3 * s:.1f}" ry="{5 * s:.1f}" fill="{INK}"/>'
                f'<path d="M{fx - 10 * s:.1f},{fy + 9 * s:.1f} q{10 * s:.1f},{9 * s:.1f} {20 * s:.1f},0" fill="none" stroke="{INK}" stroke-width="{max(2, 2.5 * s):.1f}"/>')
    return out


def sun(cx, cy, color, r, mood):
    s = ''
    n = 18
    for i in range(n):  # sunburst wedges across the sky
        a1, a2 = 2 * math.pi * i / n, 2 * math.pi * (i + .5) / n
        L = 900
        s += (f'<polygon points="{pts([(cx, cy), (cx + math.cos(a1) * L, cy + math.sin(a1) * L), (cx + math.cos(a2) * L, cy + math.sin(a2) * L)])}" '
              f'fill="#fff" opacity="{.16 if mood != "shiver" else .07}"/>')
    if mood == 'cool':  # wavy flame rays
        for i in range(16):
            a = 2 * math.pi * i / 16
            x1, y1 = cx + math.cos(a) * (r + 6), cy + math.sin(a) * (r + 6)
            x2, y2 = cx + math.cos(a) * (r + 34), cy + math.sin(a) * (r + 34)
            s += f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{INK}" stroke-width="11"/>'
            s += f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#ff9f1c" stroke-width="6"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" stroke="{INK}" stroke-width="5"/>'
    k = r / 60
    if mood == 'cool':
        s += (f'<path d="M{cx - 52 * k},{cy - 12 * k} h44 q-2,28 -22,28 q-20,0 -22,-28z M{cx + 8 * k},{cy - 12 * k} h44 q-2,28 -22,28 q-20,0 -22,-28z" fill="{INK}"/>'
              f'<path d="M{cx - 8 * k},{cy - 10 * k} h{16 * k} M{cx - 52 * k},{cy - 12 * k} l-14,-6 M{cx + 52 * k},{cy - 12 * k} l14,-6" stroke="{INK}" stroke-width="5"/>'
              f'<path d="M{cx - 34 * k},{cy + 26 * k} Q{cx},{cy + 54 * k} {cx + 34 * k},{cy + 26 * k}Z" fill="#7a1f1f" stroke="{INK}" stroke-width="4"/>'
              f'<path d="M{cx + 6 * k},{cy + 36 * k} q8,16 18,4" fill="#e0707a" stroke="{INK}" stroke-width="3"/>'
              + drop(cx + 56 * k, cy - 30 * k, 1.2))
    else:
        s += pie_eye(cx - 18 * k, cy - 8 * k, 6 * k, 11 * k) + pie_eye(cx + 18 * k, cy - 8 * k, 6 * k, 11 * k)
        if mood == 'shiver':
            s += f'<path d="M{cx - 22 * k},{cy + 22 * k} l7,-5 7,5 7,-5 7,5 7,-5 7,5" fill="none" stroke="{INK}" stroke-width="3.5"/>'
            s += f'<path d="M{cx - r - 12},{cy - 10} l-8,4 8,4 M{cx + r + 12},{cy - 10} l8,4 -8,4" fill="none" stroke="{INK}" stroke-width="3"/>'
        elif mood == 'calm':
            s += f'<path d="M{cx - 18 * k},{cy + 18 * k} q{18 * k},{12 * k} {36 * k},0" fill="none" stroke="{INK}" stroke-width="4"/>'
        else:
            s += f'<path d="M{cx - 30 * k},{cy + 14 * k} Q{cx},{cy + 44 * k} {cx + 30 * k},{cy + 14 * k}" fill="none" stroke="{INK}" stroke-width="5"/>'
            s += f'<ellipse cx="{cx - 34 * k}" cy="{cy + 10 * k}" rx="{8 * k}" ry="{5 * k}" fill="#e0707a" opacity=".6"/><ellipse cx="{cx + 34 * k}" cy="{cy + 10 * k}" rx="{8 * k}" ry="{5 * k}" fill="#e0707a" opacity=".6"/>'
    return s


def tree(x, by, sz, kind, crown, frozen, rng):
    s = f'<path d="M{x - sz * .13},{by} L{x - sz * .08},{by - sz * 1.15} L{x + sz * .08},{by - sz * 1.15} L{x + sz * .13},{by}Z" fill="#6b4a32" stroke="{INK}" stroke-width="3.5"/>'
    if kind == 'bare':
        branches = [(-.55, -1.75), (.5, -1.8), (-.2, -2.1), (.25, -2.15), (-.7, -1.4), (.7, -1.45)]
        for bx, byy in branches:
            ex, ey = x + bx * sz, by + byy * sz
            s += f'<path d="M{x},{by - sz * 1.05} Q{x + bx * sz * .3},{by + byy * sz * .7} {ex:.1f},{ey:.1f}" fill="none" stroke="{INK}" stroke-width="{sz * .11 + 3:.1f}"/>'
            s += f'<path d="M{x},{by - sz * 1.05} Q{x + bx * sz * .3},{by + byy * sz * .7} {ex:.1f},{ey:.1f}" fill="none" stroke="#6b4a32" stroke-width="{sz * .11:.1f}"/>'
            if frozen:
                s += f'<ellipse cx="{ex:.1f}" cy="{ey - 2:.1f}" rx="{sz * .14:.1f}" ry="{sz * .07:.1f}" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        return s
    c1, c2, _ = crown
    cs = [(x, by - sz * 1.55, sz * .7), (x - sz * .55, by - sz * 1.25, sz * .5), (x + sz * .55, by - sz * 1.25, sz * .5),
          (x - sz * .28, by - sz * 2.0, sz * .45), (x + sz * .3, by - sz * 1.95, sz * .45)]
    if kind == 'autumn':
        cs = cs[:4]
    s += blob(cs, c1, sw=4, highlight=c2)
    if kind == 'autumn':
        for _ in range(4):
            lx, ly = x + rng.uniform(-sz, sz), by - rng.uniform(0, sz)
            s += f'<ellipse cx="{lx:.0f}" cy="{ly:.0f}" rx="5" ry="3" fill="{c2}" stroke="{INK}" stroke-width="1.5" transform="rotate({rng.randint(0, 180)} {lx:.0f} {ly:.0f})"/>'
    return s


def clock_tower(frozen):
    s = ('<rect x="62" y="96" width="96" height="250" fill="#8a5a44" stroke="#1a1a1a" stroke-width="5"/>'
         '<path d="M52,100 L110,34 L168,100Z" fill="#4a5a52" stroke="#1a1a1a" stroke-width="5"/>'
         '<rect x="104" y="12" width="12" height="26" fill="#4a5a52" stroke="#1a1a1a" stroke-width="4"/>'
         '<path d="M110,4 l-8,10 h16z" fill="#c9a43a" stroke="#1a1a1a" stroke-width="3"/>'
         '<circle cx="110" cy="138" r="30" fill="#f4eedd" stroke="#1a1a1a" stroke-width="5"/>'
         '<path d="M110,138 V116 M110,138 L126,146" stroke="#1a1a1a" stroke-width="4"/>')
    s += ''.join(f'<circle cx="{110 + math.cos(a) * 24:.1f}" cy="{138 + math.sin(a) * 24:.1f}" r="2" fill="#1a1a1a"/>'
                 for a in [i * math.pi / 6 for i in range(12)])
    for row in range(3):
        for col in range(2):
            x, y = 80 + col * 40, 190 + row * 46
            s += f'<path d="M{x},{y + 30} v-20 a10,10 0 0 1 20,0 v20z" fill="#2d3a40" stroke="#1a1a1a" stroke-width="3.5"/>'
    s += ''.join(f'<line x1="62" y1="{y}" x2="158" y2="{y}" stroke="#1a1a1a" stroke-width="2" opacity=".35"/>' for y in range(110, 346, 22))
    if frozen:
        s += '<path d="M48,102 Q70,88 110,40 Q150,88 172,102 Q110,96 48,102Z" fill="#fff" stroke="#1a1a1a" stroke-width="3"/>'
    return s


def bridge(frozen):
    s = ''
    for px in (640, 800, 960, 1120):
        s += f'<path d="M{px - 14},244 h28 l6,70 h-40z" fill="#9a8f80" stroke="{INK}" stroke-width="4"/>'
    s += f'<rect x="520" y="232" width="700" height="14" fill="#5a5f63" stroke="{INK}" stroke-width="4"/>'
    top = 190
    s += f'<polyline points="560,232 590,{top} 1220,{top}" fill="none" stroke="{INK}" stroke-width="7"/>'
    s += f'<polyline points="560,232 590,{top} 1220,{top}" fill="none" stroke="#5a5f63" stroke-width="3"/>'
    for i, x in enumerate(range(590, 1220, 40)):
        s += f'<line x1="{x}" y1="{top}" x2="{x}" y2="232" stroke="{INK}" stroke-width="3"/>'
        s += f'<line x1="{x}" y1="{top if i % 2 else 232}" x2="{x + 40}" y2="{232 if i % 2 else top}" stroke="{INK}" stroke-width="3"/>'
    if frozen:
        s += ''.join(f'<path d="M{x},246 l4,14 l4,-14z" fill="#e8f4fb" stroke="{INK}" stroke-width="1.5"/>' for x in range(530, 1200, 26))
        s += f'<rect x="586" y="{top - 6}" width="634" height="6" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    return s


def lamp(x, by):
    return (f'<rect x="{x - 3}" y="{by - 80}" width="6" height="80" fill="{INK}"/>'
            f'<path d="M{x - 10},{by - 80} h20 l-4,-18 h-12z" fill="#f4e3a1" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M{x - 12},{by - 98} h24 l-12,-8z" fill="{INK}"/>')


def background(name):
    c = SEASONS[name]
    rng = random.Random(name)
    frozen, heat = c.get('frozen', False), c.get('heat', False)
    defs = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["sky"][0]}"/>'
            f'<stop offset="1" stop-color="{c["sky"][1]}"/></linearGradient>')
    b = '<rect width="1200" height="400" fill="url(#sky)"/>'
    sc, sr, mood = c['sun']
    b += sun(820, 96, sc, sr, mood)
    cloud_spots = [(980, 70, 1.1), (330, 60, 1.0), (1110, 140, .8), (560, 110, .7), (220, 150, .6)]
    for x, y, s in cloud_spots[:c['clouds']]:
        b += bg_cloud(x, y, s, '#e9edf0' if frozen else '#fbfaf5')
    b += f'<path d="M0,240 Q150,190 330,215 Q520,180 700,212 Q900,178 1200,206 V300 H0Z" fill="{c["hills"]}" stroke="{INK}" stroke-width="3" opacity=".9"/>'
    # river
    b += f'<path d="M420,400 Q500,300 620,262 L1200,250 V400Z" fill="{c["river"]}" stroke="{INK}" stroke-width="4"/>'
    if frozen:
        b += ''.join(f'<path d="M{x},{y} l{rng.randint(-30, 30)},{rng.randint(8, 20)} l{rng.randint(10, 40)},{rng.randint(-6, 10)}" fill="none" stroke="#fff" stroke-width="2.5"/>'
                     for x, y in [(rng.randint(620, 1180), rng.randint(270, 380)) for _ in range(14)])
    else:
        for _ in range(26):
            x, y = rng.randint(560, 1180), rng.randint(272, 392)
            b += f'<path d="M{x},{y} q8,-6 16,0 t16,0" fill="none" stroke="#f4f8fb" stroke-width="3" opacity=".85"/>'
    b += bridge(frozen)
    # land + footpath
    b += f'<path d="M0,250 Q200,230 400,258 Q500,290 470,400 H0Z" fill="{c["ground"]}" stroke="{INK}" stroke-width="4"/>'
    b += f'<path d="M150,400 Q190,330 140,300 Q110,280 160,262 L190,262 Q160,284 196,306 Q252,344 240,400Z" fill="{c["path"]}" stroke="{INK}" stroke-width="3.5"/>'
    b += clock_tower(frozen)
    # fence along the riverbank
    b += f'<path d="M300,300 Q400,300 470,330" fill="none" stroke="{INK}" stroke-width="4"/>'
    b += ''.join(f'<line x1="{x}" y1="{290 + (x - 300) * .12:.0f}" x2="{x}" y2="{312 + (x - 300) * .2:.0f}" stroke="{INK}" stroke-width="4"/>'
                 for x in range(300, 470, 24))
    trees = [(240, 262, 40), (420, 262, 34), (30, 300, 46), (330, 300, 52), (470, 290, 30), (250, 370, 64), (400, 380, 56)]
    for x, by, sz in sorted(trees, key=lambda t: t[1]):
        b += tree(x, by, sz, c['tree'], c['crown'], frozen, rng)
    b += lamp(205, 330) + lamp(290, 372)
    if frozen:
        b += ''.join(f'<circle cx="{rng.randint(0, 1200)}" cy="{rng.randint(0, 400)}" r="{rng.uniform(2, 4.5):.1f}" fill="#fff" stroke="{INK}" stroke-width="1"/>' for _ in range(70))
    if heat:
        for i in range(9):
            x, y = 100 + i * 125, 180 + (i % 3) * 30
            b += f'<path d="M{x},{y} q10,-10 0,-20 t0,-20 t0,-20" fill="none" stroke="#fff" stroke-width="3" opacity=".6"/>'
    if name == 'chilly':
        for _ in range(12):
            x, y = rng.randint(0, 1200), rng.randint(40, 300)
            b += f'<ellipse cx="{x}" cy="{y}" rx="6" ry="3" fill="#d9a03a" stroke="{INK}" stroke-width="1.5" transform="rotate({rng.randint(0, 180)} {x} {y})"/>'
    return svg(1200, 400, b, defs)


# ----------------------------------------------------------------- weather overlays
def big_cloud(fill, mood):
    cs = [(150, 190, 70), (240, 150, 92), (345, 180, 76), (200, 238, 62), (300, 240, 66), (100, 245, 46), (400, 240, 48)]
    s = blob(cs, fill, sw=10, highlight='#ffffff')
    fx, fy = 250, 200
    if mood == 'sad':
        s += f'<path d="M208,180 l28,-12 M292,180 l-28,-12" stroke="{INK}" stroke-width="6"/>'
        s += pie_eye(222, 200, 10, 17) + pie_eye(278, 200, 10, 17)
        s += f'<path d="M232,244 q18,-14 36,0" fill="none" stroke="{INK}" stroke-width="6"/>'
        s += drop(204, 222, .9)
    elif mood == 'happy':
        s += pie_eye(222, 196, 10, 17) + pie_eye(278, 196, 10, 17)
        s += f'<path d="M226,232 Q250,258 274,232" fill="none" stroke="{INK}" stroke-width="6"/>'
        s += f'<ellipse cx="200" cy="226" rx="13" ry="7" fill="#e0707a" opacity=".55"/><ellipse cx="300" cy="226" rx="13" ry="7" fill="#e0707a" opacity=".55"/>'
    elif mood == 'angry':
        s += f'<path d="M204,168 l34,16 M296,168 l-34,16" stroke="{INK}" stroke-width="8"/>'
        s += pie_eye(224, 204, 10, 14) + pie_eye(276, 204, 10, 14)
        s += f'<path d="M222,244 h56 v14 h-56z" fill="#fff" stroke="{INK}" stroke-width="5"/>'
        s += ''.join(f'<line x1="{x}" y1="244" x2="{x}" y2="258" stroke="{INK}" stroke-width="3"/>' for x in (236, 250, 264))
    return s


def snowflake(x, y, r):
    s = ''
    for i in range(3):
        a = math.pi / 3 * i
        dx, dy = math.cos(a) * r, math.sin(a) * r
        s += f'<line x1="{x - dx:.1f}" y1="{y - dy:.1f}" x2="{x + dx:.1f}" y2="{y + dy:.1f}" stroke="{INK}" stroke-width="7"/>'
        s += f'<line x1="{x - dx:.1f}" y1="{y - dy:.1f}" x2="{x + dx:.1f}" y2="{y + dy:.1f}" stroke="#fff" stroke-width="3.5"/>'
    return s


def overlay(kind):
    rng = random.Random(kind)
    if kind == 'rain':
        b = big_cloud('#c9ced4', 'sad')
        for x, y in [(130, 310), (190, 340), (250, 315), (310, 350), (370, 312), (160, 410), (280, 420), (350, 400), (220, 460)]:
            b += drop(x, y, 1.4, '#7fb0d6')
    elif kind == 'snow':
        b = big_cloud('#f1f5f8', 'happy')
        b += beanie(240, 40, 62, '#b8322a')
        for x, y in [(130, 320), (200, 360), (270, 320), (340, 360), (390, 310), (160, 430), (300, 440), (380, 420)]:
            b += snowflake(x, y, rng.uniform(14, 20))
    elif kind == 'hail':
        b = big_cloud('#8f98a3', 'angry')
        b += f'<path d="M330,280 l-30,60 h28 l-24,62 l64,-84 h-30 l26,-38z" fill="#f2c94c" stroke="{INK}" stroke-width="5"/>'
        for x, y in [(130, 320), (190, 370), (250, 330), (390, 330), (160, 440), (250, 430), (420, 420)]:
            r = rng.uniform(13, 19)
            poly = [(x + math.cos(a) * r * rng.uniform(.75, 1.1), y + math.sin(a) * r * rng.uniform(.75, 1.1))
                    for a in [i * 2 * math.pi / 7 for i in range(7)]]
            b += f'<polygon points="{pts(poly)}" fill="#dceef8" stroke="{INK}" stroke-width="4"/>'
            b += f'<path d="M{x - r * .4:.0f},{y - r * .3:.0f} l{r * .3:.0f},{-r * .2:.0f}" stroke="#fff" stroke-width="3"/>'
    else:  # tornado
        b = ''
        n = 15
        for i in range(n - 1, -1, -1):
            t = i / (n - 1)
            y = 60 + t * 380
            rx = 20 + 190 * (1 - t) ** 1.4
            x = 250 + math.sin(t * 5) * 30 * t
            b += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{8 + 18 * (1 - t):.1f}" fill="#a39b8e" stroke="{INK}" stroke-width="5"/>'
            b += f'<path d="M{x - rx * .6:.1f},{y + 3:.1f} Q{x:.1f},{y + 12 * (1 - t) + 6:.1f} {x + rx * .5:.1f},{y + 2:.1f}" fill="none" stroke="#e7e1d4" stroke-width="3" opacity=".8"/>'
        b += f'<path d="M190,104 l36,14 M310,104 l-36,14" stroke="{INK}" stroke-width="8"/>'
        b += pie_eye(214, 136, 10, 14) + pie_eye(286, 136, 10, 14)
        b += f'<path d="M220,180 Q250,160 280,180 Q250,172 220,180Z" fill="{INK}" stroke="{INK}" stroke-width="5"/>'
        for x, y, a in [(120, 300, 20), (380, 260, -30), (150, 420, 60), (360, 400, 10), (420, 340, 45)]:
            b += f'<rect x="{x - 18}" y="{y - 5}" width="36" height="10" fill="#8a5a3c" stroke="{INK}" stroke-width="3" transform="rotate({a} {x} {y})"/>'
        b += f'<circle cx="90" cy="380" r="8" fill="#9a8f80" stroke="{INK}" stroke-width="3"/><circle cx="410" cy="200" r="6" fill="#9a8f80" stroke="{INK}" stroke-width="3"/>'
    return svg(500, 500, b)


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {}
    for t in OUTFITS:
        files[f'char-{t}.svg'] = character(t)
        files[f'bg-{t}.svg'] = background(t)
    for k in ('rain', 'snow', 'hail', 'tornado'):
        files[f'overlay-{k}.svg'] = overlay(k)
    for name, data in files.items():
        with open(os.path.join(OUT, name), 'w') as f:
            f.write(data)
    print(f'wrote {len(files)} files to {os.path.normpath(OUT)}')


if __name__ == '__main__':
    main()
