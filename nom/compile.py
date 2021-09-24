import re
import os
import shutil
from nom import md2html, parsers
from jinja2 import FileSystemLoader, environment

MATH_RE = re.compile('(^\$\$|¦)', re.M)

dir = os.path.dirname(os.path.abspath(__file__))
templ_dir = os.path.join(dir, 'templates')
static_dir = os.path.join(dir, 'static')
env = environment.Environment()
env.loader = FileSystemLoader(templ_dir)


def compile_note(note, outdir, stylesheet=None, templ='default', ignore_missing=False, comments=False, preview=False, copy_assets=False, templ_data=None):
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
            if copy_assets:
                shutil.copy(from_img_path, to_img_path)
            else:
                if os.path.exists(to_img_path) or os.path.islink(to_img_path):
                    os.remove(to_img_path)
                os.symlink(from_img_path, to_img_path)

            # update references to that image in the note
            to_img_path_rel = os.path.relpath(to_img_path, outdir)
            content = content.replace(img_path, to_img_path_rel)
        except FileNotFoundError:
            if not ignore_missing:
                raise
            print('Couldn\'t find `{}`, ignoring'.format(from_img_path))

    # default styles
    css_dir = os.path.join(static_dir, 'css')
    css = [open(os.path.join(css_dir, f), 'r').read() for f in os.listdir(css_dir)]

    # if a stylesheet was specified, copy it over
    if stylesheet is not None:
        css.append(open(stylesheet, 'r').read())

    # write the stylesheet
    with open(os.path.join(outdir, 'style.css'), 'w') as f:
        f.write('\n'.join(css))

    # default javascript
    js_dir = os.path.join(static_dir, 'js')
    js = [open(os.path.join(js_dir, f), 'r').read() for f in os.listdir(js_dir)]
    with open(os.path.join(outdir, 'main.js'), 'w') as f:
        f.write('\n'.join(js))

    # symlink mathjax
    include_math = MATH_RE.search(content)
    if include_math:
        to_mathjax = os.path.join(outdir, 'mathjax')
        if os.path.exists(to_mathjax) or os.path.islink(to_mathjax):
            os.remove(to_mathjax)
        os.symlink(os.path.join(static_dir, 'mathjax'), to_mathjax)

    # render
    templ_data = templ_data or {}
    html = md2html.compile_markdown(content, comments=comments)
    content = templ.render(html=html, title=title, preview=preview, **templ_data)

    # save it
    outpath = os.path.join(outdir, 'index.html')
    with open(outpath, 'w') as out:
        out.write(content)

    return outpath
