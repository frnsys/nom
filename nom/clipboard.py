import sys
import subprocess

if 'darwin' in sys.platform:
    try:
        from AppKit import NSPasteboard
    except ImportError:
        NSPasteboard = None

def get_clipboard_html():
    """returns html in clipboard, if any"""
    if 'darwin' in sys.platform:
        if NSPasteboard is None:
            raise Exception('AppKit not found, first run `pip install pyobjc`')
        pb = NSPasteboard.generalPasteboard()
        return pb.stringForType_('public.html')

    elif 'linux' in sys.platform:
        res = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o', '-t', 'text/html'],
                stdout=subprocess.PIPE)
        return res.stdout.decode('utf8')

    else:
        raise Exception('Platform "{}" is not supported'.format(sys.platform))
