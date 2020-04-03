import os
import sys
import click
from functools import partial
from nom import html2md, md2html, parsers, compile, util
from nom.watch import watch_note
from nom.server import MarkdownServer
from nom.clipboard import get_clipboard_html
from nom.compile import env

@click.group()
def cli():
    pass


def compile_note(note, outdir, watch=False, watch_port=9001,
                 view=False, style=None, templ='default', ignore_missing=False, comments=False):
    note = util.abs_path(note)
    f = partial(compile.compile_note,
                outdir=outdir,
                templ=templ,
                stylesheet=style,
                ignore_missing=ignore_missing,
                comments=comments,
                preview=True)
    outpath = f(note)
    if view:
        click.launch(outpath)
    if watch:
        server = MarkdownServer(watch_port)
        server.start()
        def handler(note):
            f(note)
            server.update_clients()
        watch_note(note, handler)
        server.shutdown()
    return outpath


@cli.command()
@click.argument('notedir')
@click.option('-i', '--ignore-missing', is_flag=True, help='ignore missing assets')
def browse(notedir, ignore_missing):
    """browse a note directory in the browser"""
    templ = env.get_template('browser.html')
    for root, dirs, files in os.walk(notedir):
        index = []
        outdir = os.path.join('/tmp', 'nom', root)
        os.makedirs(outdir, exist_ok=True)
        for f in files:
            if not f.endswith('.md'): continue
            notepath = os.path.join(root, f)
            compile_note(notepath, outdir, view=False, ignore_missing=ignore_missing)
            index.append(f.replace('.md', ''))

        dirs = [d for d in dirs if d != 'assets']
        html = templ.render(notes=index, dirs=dirs)
        with open(os.path.join(outdir, 'index.html'), 'w') as f:
            f.write(html)
    click.launch('/tmp/nom/index.html')


@cli.command()
@click.argument('note')
@click.option('-w', '--watch', is_flag=True, help='watch the note for changes')
@click.option('-p', '--watch-port', help='watch server port', default=9001)
@click.option('-i', '--ignore-missing', is_flag=True, help='ignore missing assets')
@click.option('-s', '--style', help='stylesheet to use', default=None)
@click.option('-t', '--templ', help='template to use', default='default')
def view(note, **kwargs):
    """view a note in the browser"""
    compile_note(note, '/tmp', view=True, **kwargs)


@cli.command()
@click.argument('note')
@click.argument('outdir')
@click.option('-w', '--watch', is_flag=True, help='watch the note for changes')
@click.option('-p', '--watch-port', help='watch server port', default=9001)
@click.option('-v', '--view', is_flag=True, help='view the note in the browser')
@click.option('-s', '--style', help='stylesheet to use', default=None)
def export(note, outdir, **kwargs):
    """export a note to html"""
    compile_note(note, outdir, **kwargs)


@cli.command()
@click.argument('note')
@click.option('-o', '--outdir', default='/tmp')
@click.option('-w', '--watch', is_flag=True, help='watch the note for changes')
@click.option('-p', '--watch-port', help='watch server port', default=9001)
@click.option('-v', '--view', is_flag=True, help='view the note in the browser')
@click.option('-s', '--style', help='stylesheet to use', default=None)
def preach(note, outdir, **kwargs):
    """export a note to an html presentation"""
    compile_note(note, outdir, templ='preach', comments=True, **kwargs)


@cli.command()
@click.option('-s', '--save', help='note path to save to. will download images')
@click.option('-e', '--edit', is_flag=True, help='edit the note after saving')
@click.option('-v', '--view', is_flag=True, help='view the note in the browser')
@click.option('-o', '--overwrite', is_flag=True, help='overwrite existing note')
def clip(save, edit, view, overwrite):
    """convert html in the clipboard to markdown"""
    path = save
    html = get_clipboard_html()
    if html is None:
        click.echo('No html in the clipboard')
        return

    if path is None:
        content = html2md.html_to_markdown(html).strip()
        click.echo(content)
        return

    if not path.endswith('.md'):
        click.echo('Note must have extension ".md"')
        return

    note = util.abs_path(path)
    if os.path.exists(note) and not overwrite:
        click.echo('Note already exists at "{}" (specify `--overwrite` to overwrite)'.format(note))
        return

    html = parsers.rewrite_external_images(html, note)
    content = html2md.html_to_markdown(html).strip()
    with open(note, 'w') as f:
        f.write(content)

    if edit:
        click.edit(filename=note)

    if view:
        compile_note(note, '/tmp', view=True)


@cli.command()
def convert():
    """convert markdown from stdin to html"""
    md = sys.stdin.read()
    print(md2html.compile_markdown(md))


@cli.command()
@click.argument('notes', nargs=-1, type=click.Path(exists=True))
@click.option('-s', '--separator', default='===')
def concat(notes, separator):
    """concatenate multiple notes"""
    agg = []
    for n in notes:
        agg.append(open(n, 'r').read())
    print('\n{}\n'.format(separator).join(agg))
