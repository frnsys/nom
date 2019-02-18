import os
import shutil
from nom import md2html, parsers
from jinja2 import FileSystemLoader, environment


dir = os.path.dirname(os.path.abspath(__file__))
templ_dir = os.path.join(dir, 'templates')
env = environment.Environment()
env.loader = FileSystemLoader(templ_dir)


def compile_note(note, outdir, stylesheet=None, templ='default', ignore_missing=False, comments=False, preview=False):
    title, _ = os.path.basename(note).rsplit('.', 1)
    content = open(note, 'r').read()
    if templ.endswith('.html'):
        templ = env.from_string(open(templ, 'r').read())
    else:
        templ = env.get_template('{}.html'.format(templ))

    # create output directory if necessary
    outdir = os.path.join(outdir, title)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # create assets directory if necessary
    assetsdir = os.path.join(outdir, 'assets')
    if not os.path.exists(assetsdir):
        os.makedirs(assetsdir)

    # copy over any local images
    for img_path in parsers.md_images(content):
        # assume http indicates remote image
        if img_path.startswith('http'):
            continue

        # copy img to compiled assets directory
        _, img_name = os.path.split(img_path)
        to_img_path = os.path.join(assetsdir, img_name)
        from_img_path = os.path.join(os.path.dirname(note), img_path)
        try:
            shutil.copy(from_img_path, to_img_path)

            # update references to that image in the note
            to_img_path_rel = os.path.relpath(to_img_path, outdir)
            content = content.replace(img_path, to_img_path_rel)
        except FileNotFoundError:
            if not ignore_missing:
                raise
            print('Couldn\'t find `{}`, ignoring'.format(from_img_path))

    # default styles
    styles = open(os.path.join(templ_dir, 'style.css'), 'r').read()

    # if a stylesheet was specified, copy it over
    if stylesheet is not None:
        styles = '\n'.join([styles, open(stylesheet, 'r').read()])

    # write the stylesheet
    with open(os.path.join(outdir, 'style.css'), 'w') as f:
        f.write(styles)

    # render
    html = md2html.compile_markdown(content, comments=comments)
    content = templ.render(html=html, title=title, preview=preview)

    # save it
    outpath = os.path.join(outdir, 'index.html')
    with open(outpath, 'w') as out:
        out.write(content)

    return outpath
