import time
from os import path
from nom import util
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def watch_notes(notes, handle_func):
    """watch a notes for changes,
    call `handle_func` on change"""
    ob = Observer()
    handler = FileSystemEventHandler()
    dirs = set(path.dirname(n) for n in notes)
    notes = [
        (n, path.basename(n), path.normpath(util.assets_dir(n)))
        for n in notes]

    def handle_event(event):
        _, filename = path.split(event.src_path)
        src_path = path.normpath(event.src_path)
        note = next((n[0] for n in notes if n[1] == filename or n[2] == src_path), None)
        if note is not None:
            print('compiling {}'.format(note))
            handle_func(note)
            print('done')
    handler.on_any_event = handle_event

    print('watching')
    for d in dirs:
        ob.schedule(handler, d, recursive=True)
    ob.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('stopping...')
        ob.stop()
    ob.join()
