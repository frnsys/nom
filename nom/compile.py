import os
import shutil
from nom import md2html, parsers
from jinja2 import FileSystemLoader, environment


dir = os.path.dirname(os.path.abspath(__file__))
env = environment.Environment()
env.loader = FileSystemLoader(os.path.join(dir, 'templates'))


def compile_note(note, outdir, templ='default'):
    title, _ = os.path.basename(note).rsplit('.', 1)
    content = open(note, 'r').read()
    templ = env.get_template('{}.html'.format(templ))

    # create output directory if necessary
    outdir = os.path.join(outdir, title)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # copy over any images
    for img in parsers.md_images(content):
        img_path = os.path.join(outdir, img)
        img_dir = os.path.dirname(img_path)

        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        shutil.copy(os.path.join(os.path.dirname(note), img), img_path)

    # render the presentation
    html = md2html.compile_markdown(content)
    content = templ.render(html=html)

    # save it
    outpath = os.path.join(outdir, 'index.html')
    with open(outpath, 'w') as out:
        out.write(content)

    return outpath
