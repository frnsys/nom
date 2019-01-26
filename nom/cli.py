import os
import sys
import click
from functools import partial
from nom import html2md, md2html, parsers, compile, util
from nom.watch import watch_note
from nom.server import MarkdownServer
from nom.clipboard import get_clipboard_html

@click.group()
def cli():
    pass


def compile_note(note, outdir, watch=False, view=False, style=None, templ='default', ignore_missing=False, comments=False):
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
        server = MarkdownServer()
        server.start()
        def handler(note):
            f(note)
            server.update_clients()
        watch_note(note, handler)
        server.shutdown()
    return outpath


@cli.command()
@click.argument('note')
@click.option('-w', '--watch', is_flag=True, help='watch the note for changes')
@click.option('-i', '--ignore', is_flag=True, help='ignore missing assets')
@click.option('-s', '--style', help='stylesheet to use', default=None)
@click.option('-t', '--templ', help='template to use', default='default')
def view(note, watch, ignore, style, templ):
    """view a note in the browser"""
    compile_note(note, '/tmp', view=True, watch=watch, ignore_missing=ignore, style=style, templ=templ)


@cli.command()
@click.argument('note')
@click.argument('outdir')
@click.option('-w', '--watch', is_flag=True, help='watch the note for changes')
@click.option('-v', '--view', is_flag=True, help='view the note in the browser')
@click.option('-s', '--style', help='stylesheet to use', default=None)
def export(note, outdir, watch, view, style):
    """export a note to html"""
    compile_note(note, outdir, watch=watch, view=view, style=style)


@cli.command()
@click.argument('note')
@click.option('-o', '--outdir', default='/tmp')
@click.option('-w', '--watch', is_flag=True, help='watch the note for changes')
@click.option('-v', '--view', is_flag=True, help='view the note in the browser')
@click.option('-S', '--static', is_flag=True, help='compile as static presentation')
@click.option('-s', '--style', help='stylesheet to use', default=None)
def preach(note, outdir, watch, view, static, style):
    """export a note to an html presentation"""
    path = compile_note(note, outdir, watch=watch, view=view, style=style, templ='preach', comments=True)
    if static:
        with open(path, 'r') as f:
            data = f.read()
        data = data.replace('static = false', 'static = true')
        print(data)
        with open(path, 'w') as f:
            f.write(data)


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
