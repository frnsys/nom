import sys

if 'darwin' in sys.platform:
    try:
        from AppKit import NSPasteboard
    except ImportError:
        NSPasteboard = None
elif 'linux' in sys.platform:
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gdk
    except ImportError:
        Gtk = None


def get_clipboard_html():
    """returns html in clipboard, if any"""
    if 'darwin' in sys.platform:
        if NSPasteboard is None:
            raise Exception('AppKit not found, first run `pip install pyobjc`')
        pb = NSPasteboard.generalPasteboard()
        return pb.stringForType_('public.html')

    elif 'linux' in sys.platform:
        if Gtk is None:
            raise Exception('Could not import GTK, is it installed on this system?')
        cb = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        html_target = Gdk.Atom.intern('text/html', False)
        targets = cb.wait_for_targets()[1]
        if html_target not in targets:
            return None
        return cb.wait_for_contents(html_target).get_data()

    else:
        raise Exception('Platform "{}" is not supported'.format(sys.platform))
