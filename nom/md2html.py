"""
https://python-markdown.github.io/extensions/api/
"""

import re
import base64
import markdown
import subprocess
from markdown.util import etree, AMP_SUBSTITUTE
from markdown.extensions import attr_list
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor
from markdown.inlinepatterns import Pattern, SimpleTagPattern, ImagePattern
from mdx_gfm import GithubFlavoredMarkdownExtension as GFM

AT = attr_list.AttrListTreeprocessor()


def compile_markdown(md, comments=False):
    """compiles markdown to html"""
    extensions = [
        GFM(),
        NomMD(),
        EmDashExtension(),
        MathJaxExtension(),
        SortFootnotesExtension(),
        FigureCaptionExtension(),
        InlineGraphvizExtension(),
        BreakQuotesExtension(),
        'markdown.extensions.footnotes',
        'markdown.extensions.attr_list',
        'markdown.extensions.headerid',
    ]
    if comments:
        extensions.append(CommentExtension())
    return markdown.markdown(md, extensions=extensions, lazy_ol=False)


class PDFPattern(ImagePattern):
    def handleMatch(self, m):
        src = m.group(3)
        fig = etree.Element('figure')

        obj = etree.SubElement(fig, 'iframe')
        obj.set('src', src)

        a = etree.SubElement(fig, 'a')
        a.set('href', src)
        a.text = m.group(2) or src.split('/')[-1]

        return fig


class VideoPattern(ImagePattern):
    def handleMatch(self, m):
        src = m.group(3)
        fig = etree.Element('figure')
        obj = etree.SubElement(fig, 'video')
        obj.set('src', src)

        attrs = m.group(5)
        caption = m.group(2)
        if caption:
            cap = etree.SubElement(fig, 'figcaption')
            cap.text = caption
        if attrs is not None:
            AT.assign_attrs(obj, attrs)
        return fig


class IFramePattern(ImagePattern):
    def handleMatch(self, m):
        src = m.group(3)
        obj = etree.Element('iframe')
        obj.set('src', src)

        attrs = m.group(5)
        if attrs is not None:
            AT.assign_attrs(obj, attrs)
        return obj


class NomMD(markdown.Extension):
    """an extension that supports:
    - highlighting with the <mark> tag.
    - pdf embedding with the <iframe> tag.
    """
    HIGHLIGHT_RE = r'(={2})(.+?)(={2})' # ==highlight==
    PDF_RE = r'\!\[([^\[\]]*)\]\(`?(?:<.*>)?([^`\(\)]+pdf)(?:<\/.*>)?`?\)' # ![...](path/to/something.pdf)
    VID_RE = r'\!\[(.*)\]\(`?(?:<.*>)?([^`\(\)]+mp4)\)({:([^}]+)})?' # ![...](path/to/something.mp4){: autoplay}
    URL_RE = r'@\[(.*)\]\(`?(?:<.*>)?([^`\(\)]+)\)({:([^}]+)})?' # @[](http://web.site){: .fullscreen}

    def extendMarkdown(self, md, md_globals):
        highlight_pattern = SimpleTagPattern(self.HIGHLIGHT_RE, 'mark')
        md.inlinePatterns.add('highlight', highlight_pattern, '_end')

        pdf_pattern = PDFPattern(self.PDF_RE)
        md.inlinePatterns.add('pdf_link', pdf_pattern, '_begin')

        vid_pattern = VideoPattern(self.VID_RE)
        md.inlinePatterns.add('video_link', vid_pattern, '_begin')

        url_pattern = IFramePattern(self.URL_RE)
        md.inlinePatterns.add('iframe_link', url_pattern, '_begin')


"""
from <https://github.com/mayoff/python-markdown-mathjax>
"""
class MathJaxPattern(markdown.inlinepatterns.Pattern):
    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        return node

class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')


"""
compile html comments into elements,
for preach presenter notes
"""
class CommentProcessor(Postprocessor):
    COMMENTS_RE = re.compile('<!--(((?!-->).)+)-->', re.DOTALL)
    def run(self, text):
        return self.COMMENTS_RE.sub(self.compile_comment, text)

    def compile_comment(self, match):
        text = match.group(1)
        html = compile_markdown(text)
        return '\n<div class="comment">\n{}\n</div>'.format(html)

class CommentExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('commentAltExtension',
                                CommentProcessor(md.parser),
                                '>raw_html')


"""
The below is from: <https://github.com/jdittrich/figureAltCaption>
(Not provided as a pypi package, so reproduced here)

Generates a Caption for Figures for each Image which stands alone in a paragraph,
similar to pandoc#s handling of images/figures

--------------------------------------------

Licensed under the GPL 2 (see LICENSE.md)

Copyright 2015 - Jan Dittrich by
building upon the markdown-figures Plugin by
Copyright 2013 - [Helder Correia](http://heldercorreia.com) (GPL2)
"""
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import IMAGE_LINK_RE, IMAGE_REFERENCE_RE
FIGURES = [u'^\s*'+IMAGE_LINK_RE+u'\s*$', u'^\s*'+IMAGE_REFERENCE_RE+u'\s*$'] #is: linestart, any whitespace (even none), image, any whitespace (even none), line ends.


# This is the core part of the extension
class FigureCaptionProcessor(BlockProcessor):
    FIGURES_RE = re.compile('|'.join(f for f in FIGURES))
    def test(self, parent, block): # is the block relevant
        isImage = bool(self.FIGURES_RE.search(block))
        isOnlyOneLine = (len(block.splitlines())== 1)
        isInFigure = (parent.tag == 'figure')

        # print(block, isImage, isOnlyOneLine, isInFigure, "T,T,F")
        if (isImage and isOnlyOneLine and not isInFigure):
            return True
        else:
            return False

    def run(self, parent, blocks): # how to process the block?
        raw_block = blocks.pop(0)
        captionText = self.FIGURES_RE.search(raw_block).group(1)

        # create figure
        figure = etree.SubElement(parent, 'figure')

        # render image in figure
        figure.text = raw_block

        # create caption
        figcaptionElem = etree.SubElement(figure,'figcaption')
        figcaptionElem.text = captionText #no clue why the text itself turns out as html again and not raw. Anyhow, it suits me, the blockparsers annoyingly wrapped everything into <p>.


class FigureCaptionExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        """ Add an instance of FigcaptionProcessor to BlockParser. """
        md.parser.blockprocessors.add('figureAltcaption',
                                      FigureCaptionProcessor(md.parser),
                                      '<ulist')


# InlineGraphViz, from <https://github.com/sprin/markdown-inline-graphviz>
BLOCK_RE = re.compile(
    r'^\{% (?P<command>\w+)\s+(?P<filename>[^\s]+)\s*\n(?P<content>.*?)%}\s*$',
    re.MULTILINE | re.DOTALL)
SUPPORTED_COMMAMDS = ['dot', 'neato', 'fdp', 'sfdp', 'twopi', 'circo']


class InlineGraphvizExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        """ Add InlineGraphvizPreprocessor to the Markdown instance. """
        md.preprocessors.add('graphviz_block',
                             InlineGraphvizPreprocessor(md), '_begin')

class InlineGraphvizPreprocessor(Preprocessor):
    def __init__(self, md):
        super(InlineGraphvizPreprocessor, self).__init__(md)

    def run(self, lines):
        """ Match and generate dot code blocks."""

        text = "\n".join(lines)
        while 1:
            m = BLOCK_RE.search(text)
            if m:
                command = m.group('command')
                # Whitelist command, prevent command injection.
                if command not in SUPPORTED_COMMAMDS:
                    raise Exception('Command not supported: %s' % command)
                filename = m.group('filename')
                content = m.group('content')
                filetype = filename[filename.rfind('.')+1:]

                args = [command, '-T'+filetype]
                try:
                    proc = subprocess.Popen(
                        args,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE)
                    proc.stdin.write(content.encode('utf-8'))

                    output, err = proc.communicate()

                    if filetype == 'svg':
                        data_url_filetype = 'svg+xml'
                        encoding = 'utf-8'
                        img = output.decode(encoding)

                    if filetype == 'png':
                        data_url_filetype = 'png'
                        encoding = 'base64'
                        output = base64.b64encode(output)
                        data_path = "data:image/%s;%s,%s" % (
                            data_url_filetype,
                            encoding,
                            output.decode('utf8'))
                        img = "![" + filename + "](" + data_path + ")"

                    text = '%s\n%s\n%s' % (
                        text[:m.start()], img, text[m.end():])

                except Exception as e:
                        err = str(e) + ' : ' + str(args)
                        return (
                            '<pre>Error : ' + err + '</pre>'
                            '<pre>' + content + '</pre>').split('\n')
            else:
                break
        return text.split("\n")


FOOTNOTE_REF_RE = re.compile('\[\^([A-Za-z0-9]+)\]') # [^id]
FOOTNOTE_DEF_RE = re.compile('^\[\^([A-Za-z0-9]+)\]:') # [^id]:
class SortFootnotesProcessor(Preprocessor):
    """Sort footnote definitions according to footnote
    reference order. Note that this moves all footnote
    definitions to the end of the document."""
    def __init__(self, md):
        super(SortFootnotesProcessor, self).__init__(md)

    def run(self, lines):
        new_lines = []
        refs = []
        defs = []
        for line in lines:
            if FOOTNOTE_DEF_RE.match(line):
                fn = FOOTNOTE_DEF_RE.match(line).group(1)
                defs.append((fn, line))
            else:
                for fn in FOOTNOTE_REF_RE.findall(line):
                    refs.append(fn)
                new_lines.append(line)

        def sort_key(fn_def):
            fn, _ = fn_def
            try:
                return refs.index(fn)
            except ValueError:
                return len(refs)

        defs = [line for fn, line in sorted(defs, key=sort_key)]
        new_lines += defs
        return new_lines

class SortFootnotesExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('sort_footnotes',
                             SortFootnotesProcessor(md), '_begin')

class BreakQuotesProcessor(Preprocessor):
    def __init__(self, md):
        super(BreakQuotesProcessor, self).__init__(md)

    def run(self, lines):
        # Iterate in overlapping chunks of 3
        for i in range(len(lines)):
            try:
                a, b, c = lines[i:i+3]
                # If white space between two quotes,
                # insert some text to force a proper line break
                if a.startswith('>') and c.startswith('>') and b.strip() == '':
                    lines[i+1] = '\n<!-- -->'
            except ValueError:
                # Less than 3 items
                pass
        return lines

class BreakQuotesExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('break_quotes',
                             BreakQuotesProcessor(md), '_begin')


# Modified from the `markdown-emdash` package
class EmDashPattern(Pattern):
    """Replaces '--' with '&emdash;'."""
    def __init__(self):
        super(EmDashPattern, self).__init__('--')

    def handleMatch(self, m):
        # have to use special AMP_SUBSTITUTE character or it gets escaped
        return '{}mdash;'.format(AMP_SUBSTITUTE)

class EmDashExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('emdashpattern', EmDashPattern(), '<not_strong')
