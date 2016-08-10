import time
from os import path
from nom import util
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def watch_note(note, handle_func):
    """watch a single note for changes,
    call `handle_func` on change"""
    ob = Observer()
    handler = FileSystemEventHandler()

    def handle_event(event):
        _, filename = path.split(event.src_path)
        if note.filename == filename or \
                path.normpath(event.src_path) == path.normpath(util.assets_dir(note)):
            handle_func(note)
    handler.on_any_event = handle_event

    print('Watching {0}...'.format(util.get_title(note)))
    ob.schedule(handler, path.dirname(note), recursive=True)
    ob.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping...')
        ob.stop()
    ob.join()
