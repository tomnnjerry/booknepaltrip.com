"""Line icons drawn for Book Nepal Trip (24x24, stroke = currentColor).

One emblem per region, one per experience kind and travel style, plus UI icons.
Render with {% icon "pagoda" %} or {% icon "pagoda" "icon--lg" %}. Check them at real size on /icons/.
"""

_STUPA = ('<path d="M3 21h18"/><path d="M5 21v-2h14v2"/><path d="M6.5 19a5.5 5.5 0 0 1 11 0"/>'
          '<path d="M10 10.5h4v3h-4z"/><path d="M10.9 12h.4M12.7 12h.4"/>'
          '<path d="M10.6 10.5L12 4l1.4 6.5"/><path d="M11.1 8.5h1.8M11.5 6.5h1"/><path d="M12 4V2.5"/>')
_RHINO = ('<path d="M3 15.2c0-3 2.4-5.2 6-5.2h5.2c2.4 0 3.9 1.2 4.9 3l2.1 1.4-1 1.6h-2.1l-.5 3h-2l-.4-2.4H10l-.5 2.4h-2l-.4-2.5C4.6 17.6 3 16.6 3 15.2z"/>'
          '<path d="M19.6 13.3l1.6-2.6"/><path d="M15.4 10.2l.7-1.6"/><path d="M17.4 13.1h.01"/>')
_PAGODA = ('<path d="M12 2.5v1.8"/><path d="M7.5 8L12 4.3 16.5 8"/><path d="M9.5 8v2h5V8"/>'
           '<path d="M5.5 12.6L9.3 10h5.4l3.8 2.6"/><path d="M8 12.6V15h8v-2.4"/>'
           '<path d="M3.5 18.2L7.8 15h8.4l4.3 3.2"/><path d="M6.5 18.2V21h11v-2.8"/><path d="M11 21v-1.8h2V21"/>')
_LOTUS = ('<path d="M12 18.5c-2-2.5-2-6 0-9 2 3 2 6.5 0 9z"/>'
          '<path d="M12 18.5c-3.5 0-6.5-2-7.5-5.5 3.5-.5 6 1.5 7.5 5.5z"/>'
          '<path d="M12 18.5c3.5 0 6.5-2 7.5-5.5-3.5-.5-6 1.5-7.5 5.5z"/><path d="M4 21.5h16"/>')
_LAKE = ('<path d="M12 3v9"/><path d="M9 4.5V7a3 3 0 0 0 6 0V4.5"/>'
         '<ellipse cx="12" cy="17" rx="8.5" ry="3.3"/><path d="M8 17h3M13.5 18.2h3"/>')
_FEAST = ('<circle cx="12" cy="13" r="8"/><circle cx="8.3" cy="11" r="1.8"/><circle cx="12" cy="8.6" r="1.8"/>'
          '<circle cx="15.7" cy="11" r="1.8"/><path d="M8.8 16c1.2-1.6 5.2-1.6 6.4 0"/>')
_GLIDER = ('<path d="M3.5 8.5c4.5-4.5 12.5-4.5 17 0"/><path d="M3.5 8.5L12 17M20.5 8.5L12 17M9 5.6L12 17M15 5.6L12 17"/>'
           '<circle cx="12" cy="18.6" r="1.3"/>')
_POT = ('<path d="M9 5h6"/><path d="M9.5 5C6.5 7 5.5 10 6.3 14c.5 2.2 2.6 3.7 5.7 3.7s5.2-1.5 5.7-3.7c.8-4-.2-7-3.2-9"/>'
        '<path d="M4.5 21h15"/><path d="M7 19.5h10"/>')
_BOWL = ('<path d="M4 11.5h16c0 4.4-3.6 7.5-8 7.5s-8-3.1-8-7.5z"/><path d="M9 21h6"/>'
         '<path d="M17 3.5l-3.6 5.2"/><path d="M6.5 8.2c.8-.9 1.8-.9 2.6 0M5 6.4c1.6-1.6 3.6-1.6 5.2 0"/>')
_TRAIL = ('<path d="M4 21c3-1 5-3 4-5s-3-3 0-5 7-1 6-4-1.5-2.6.8-3.8"/>'
          '<path d="M17 2.8v6"/><path d="M17 2.8l3.6 1.3L17 5.4"/><path d="M2.5 21.3h6"/>')

ICONS = {
    # ---- regions
    "pagoda": _PAGODA,
    "fishtail":  # Machhapuchhre's twin summit above Phewa
        '<path d="M2.5 16.5L8.5 9l2.2 2.6L13 5.2l.8 1.4.9-2.1 1.3 4.2 5.5 7.8"/><path d="M11.2 12.4l2 1.3"/>'
        '<path d="M3 19.6c2-.8 4-.8 6 0s4 .8 6 0 4-.8 6 0"/><path d="M7 22c1.4-.5 2.8-.5 4.2 0M13 22c1.4-.5 2.8-.5 4.2 0"/>',
    "everest":
        '<path d="M2 20.5L9.4 8l3 4.2L15 5l7 15.5z"/><path d="M13.6 8.6L15 5l1.7 3.6-1.2-.6-1 1z"/>'
        '<path d="M15.6 4.4c1.6-.9 3.2-.7 4.9-1.7"/><path d="M8.3 9.9l1.6 1.4.9-.6"/>',
    "rhino": _RHINO,
    "lotus": _LOTUS,
    "chorten":
        '<path d="M4.5 21h15"/><path d="M6.5 21v-2.5h11V21"/><path d="M8 18.5v-2h8v2"/>'
        '<path d="M8.6 16.5c0-2.4 1.5-4 3.4-4s3.4 1.6 3.4 4"/><path d="M10.6 12.5V11h2.8v1.5"/>'
        '<path d="M11 11l1-5.2 1 5.2"/><path d="M11.3 9.2h1.4M11.6 7.5h.8"/><path d="M10.9 4.2a1.1 1.1 0 0 0 2.2 0"/>',
    "lake": _LAKE,
    "rhododendron":
        "".join(f'<ellipse cx="12" cy="6.4" rx="2.1" ry="3" transform="rotate({a} 12 9.6)"/>' for a in (0, 72, 144, 216, 288))
        + '<circle cx="12" cy="9.6" r=".9"/><path d="M12 14.2V22"/>'
          '<path d="M12 19c-2.6-.2-4.6-1.5-5.6-3.6 2.6-.3 4.6.9 5.6 3.6z"/><path d="M12 19c2.6-.2 4.6-1.5 5.6-3.6-2.6-.3-4.6.9-5.6 3.6z"/>',
    "rara":
        '<path d="M2 14.5L7 8.5l3 3.2 3.5-5 6.5 7.8"/><path d="M3 18c3.5 1.4 14.5 1.4 18 0"/>'
        '<path d="M6 21c2.6.7 9.4.7 12 0"/><path d="M19 14.2v-3M17.6 12.8l1.4-3.2 1.4 3.2"/>',
    # ---- experience kinds
    "heritage":
        '<path d="M3.5 21h17"/><path d="M12 2.5V4"/><path d="M8.8 13L12 4.3 15.2 13"/><path d="M8.5 21v-8h7v8"/>'
        '<path d="M11 21v-3h2v3"/><path d="M5 21v-4.5h2.5V21M16.5 21v-4.5H19V21"/><path d="M4.5 16.5l2-1.5 2 1.5M15.5 16.5l2-1.5 2 1.5"/>',
    "spiritual": _STUPA,
    "stupa": _STUPA,
    "trek": _TRAIL,
    "nature":
        '<path d="M2 19l5.2-6.2 3.2 3.4 4.4-6.2L22 19z"/><path d="M8.6 8.2a3.4 3.4 0 0 1 6.8 0"/>'
        '<path d="M12 2.8v1.4M6.4 5.2l1 1M17.6 5.2l-1 1M4.5 8.2h1.4M18.1 8.2h1.4"/>',
    "wildlife": _RHINO,
    "water":
        '<path d="M3 13.5h18l-3 3.6H6z"/><path d="M13.2 8.4l3.4 5.1"/><path d="M8.5 13.5v-2.2h4.5"/>'
        '<path d="M2 20.2c2-1 4-1 6 0s4 1 6 0 4-1 6 0"/>',
    "food": _FEAST,
    "adventure": _GLIDER,
    "craft": _POT,
    "wellness": _BOWL,
    # ---- travel styles
    "boot":
        '<path d="M6 3h6v7.5l5.6 2.8c1.6.8 2.9 2.2 3.4 4V19H4v-4.2c0-1.8.5-3.4 2-4.3z"/><path d="M4 21h17"/>'
        '<path d="M12 7h-2.4M12 10h-2.4M16.5 13.2l-1.4 2.2"/>',
    "feast": _FEAST,
    "house":
        '<path d="M3 11.5L12 4l9 7.5"/><path d="M5 10v11h14V10"/><path d="M10 21v-5h4v5"/>'
        '<path d="M7 13h2v2H7zM15 13h2v2h-2z"/><path d="M15.5 6.4V4h2v4"/>',
    "family":
        '<circle cx="7.5" cy="5" r="2"/><circle cx="16.5" cy="5" r="2"/><circle cx="12" cy="11.2" r="1.6"/>'
        '<path d="M4.5 21v-7.5c0-2 1.3-3.5 3-3.5s3 1.5 3 3.5M13.5 13.5c0-2 1.3-3.5 3-3.5s3 1.5 3 3.5V21"/>'
        '<path d="M9.8 21v-4.3c0-1.5 1-2.6 2.2-2.6s2.2 1.1 2.2 2.6V21"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.3 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>',
    "camera":
        '<path d="M3 8h4l1.6-2.5h6.8L17 8h4v11H3z"/><circle cx="12" cy="13.2" r="3.6"/><path d="M18 10.5h.01"/>',
    "glider": _GLIDER,
    "wheel": _POT,
    "leaf":
        '<path d="M5 19C4 11 9 5 19.5 4.5 20 15 14 20 5 19z"/><path d="M5 19c3-4 6.5-7.5 10.5-10"/>',
    # ---- story and data
    "altitude": '<path d="M5 3v18"/><path d="M5 6h3M5 10h2M5 14h3M5 18h2"/><path d="M10.5 18L15 9l5.5 9z"/><path d="M15 6V3l-1.5 1.5M15 3l1.5 1.5"/>',
    "oxygen": '<circle cx="9" cy="12" r="5.5"/><path d="M15.5 14.5c1.3-1.2 3.2-1.2 3.2.4 0 1.3-1.7 2-3.2 3.6h3.4"/>',
    "kettle":
        '<path d="M5 20h12"/><path d="M6 20c-.6-4.6.6-8.4 5-8.4s5.6 3.8 5 8.4"/><path d="M16.2 13.3l3.3-2.3-.4 4"/>'
        '<path d="M9 11.6c0-1.6.9-2.6 2-2.6s2 1 2 2.6"/><path d="M8 6c-.6-1 .6-1.8 0-2.8M12 6c-.6-1 .6-1.8 0-2.8"/>',
    "thermo": '<path d="M10 14.5V5a2 2 0 0 1 4 0v9.5a4 4 0 1 1-4 0z"/><path d="M12 9v7"/><path d="M16.5 6h2M16.5 9h2"/>',
    "quote": '<path d="M5 18c2.5-1 3.5-3 3.5-6H5V6h5.5v6c0 4-2 6.5-5.5 7.5zM13.5 18c2.5-1 3.5-3 3.5-6h-3.5V6H19v6c0 4-2 6.5-5.5 7.5z"/>',
    "scroll": '<path d="M3.5 7h17v10h-17z"/><circle cx="7.5" cy="12" r="1"/><circle cx="16.5" cy="12" r="1"/><path d="M10 10h4M10 12h4M10 14h3"/>',
    "people":
        '<circle cx="9" cy="7.5" r="3"/><path d="M3.5 20c0-3.4 2.5-6 5.5-6s5.5 2.6 5.5 6"/>'
        '<path d="M15.5 4.8a3 3 0 0 1 0 5.4M17.5 14.4c1.8.8 3 2.9 3 5.6"/>',
    "word": '<path d="M4 5h16v11H11l-4.5 4v-4H4z"/><path d="M8 9.5h8M8 12.5h5"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.8"/>',
    "pennant": '<path d="M5 21V3l12 7.5H9.5L17 18H5"/>',
    "tea": '<path d="M4 9h12v4.5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M16 10.5h1.5a2.5 2.5 0 0 1 0 5H15.5"/><path d="M8 3.5c-.7 1.2.7 2 0 3.2M12 3.5c-.7 1.2.7 2 0 3.2"/><path d="M3 21h14"/>',
    # ---- transport
    "plane": '<path d="M10.5 21l1.5-1v-5.5l8.5 3.5v-2.2L12 10.5V5a1.5 1.5 0 0 0-3 0v5.5L.5 15.8V18L9 14.5V20l1.5 1z" transform="translate(1.5 0)"/>',
    "car": '<path d="M4 16.5V12l2-5h12l2 5v4.5z"/><path d="M4 12h16"/><circle cx="7.5" cy="16.5" r="1.8"/><circle cx="16.5" cy="16.5" r="1.8"/>',
    "bus": '<rect x="4.5" y="3.5" width="15" height="15" rx="2"/><path d="M4.5 10.5h15M4.5 14.5h15"/><path d="M7 21v-2.5M17 21v-2.5"/><path d="M7.5 16.5h.01M16.5 16.5h.01"/>',
    "heli": '<path d="M3 4.5h14M10 4.5V7"/><path d="M6.5 7h7.5c3 0 4.5 2 4.5 4.5s-2 3.5-4.5 3.5H9c-1.5 0-2.5-1-2.5-2.5z"/><path d="M14.5 7v4H19"/><path d="M6.5 11H2.5l-1-2"/><path d="M8 18.5h9M10 15v3.5M15 15v3.5"/>',
    "walk": '<circle cx="13" cy="4" r="1.8"/><path d="M10 21l2-6 2.5 2.5V21"/><path d="M8 11l3.5-3.5 3 2.5 2.5 1"/><path d="M11.5 7.5l.5 7.5"/><path d="M18 9v12"/>',
    # ---- UI
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "book": '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/>',
    "route": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "whatsapp": '<path d="M20 12a8 8 0 0 1-11.8 7L4 20l1.1-4A8 8 0 1 1 20 12z"/><path d="M9 9.5c.3 2 2.2 4.2 4.8 4.8l1-1.2-1.8-.9-.7.7c-.9-.4-1.6-1.1-2-2l.7-.7-.8-1.8z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    "star": '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 16l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "bed": '<path d="M3 19V6M3 15h18v4M21 15v-3a3 3 0 0 0-3-3h-7v6"/><circle cx="7" cy="11" r="2"/>',
    "map": '<path d="M3 6l6-2.5 6 2.5 6-2.5v14.5L15 20.5l-6-2.5L3 20.5z"/><path d="M9 3.5V18M15 6v14.5"/>',
    "check": '<path d="M4.5 12.5l5 5 10-11"/>',
}

# how_to_reach "mode" -> icon
MODE_ICONS = {"air": "plane", "flight": "plane", "road": "car", "private car": "car", "jeep": "car", "car": "car",
              "bus": "bus", "local bus": "bus", "tourist bus": "bus", "on foot": "walk", "walk": "walk", "trek": "walk",
              "helicopter": "heli", "heli": "heli", "boat": "water", "rail": "bus", "train": "bus"}


def svg(name, cls=""):
    body = ICONS.get(name) or ICONS["sparkle"]
    return (f'<svg class="icon {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def mode_icon(mode):
    m = (mode or "").lower()
    for k, v in MODE_ICONS.items():
        if k in m:
            return v
    return "route"
