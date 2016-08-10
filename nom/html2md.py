import re
import html2text
from lxml.html import builder, fromstring, tostring, clean


h2t = html2text.HTML2Text()
h2t.body_width = 0 # don't wrap lines
h2t.ul_item_mark = '-'
to_md = h2t.handle


def html_to_markdown(html):
    """convert html to markdown.
    this will try and convert span styling
    to the proper tags as well.

    e.g. `<span style='font-weight:bold;'>foo</span>`
    will become `<strong>foo</strong>`.
    """
    h = fromstring(html)

    clean_highlighted_code(h)
    for span in h.findall('.//span') + h.findall('.//font'):
        convert_span(span)

    html = tostring(h).decode('utf-8')

    # not ideal but works in a pinch
    html = html.replace('<mark>', '==')
    html = html.replace('</mark>', '==')

    md = to_md(html)

    # sometimes html2text returns a ton of extra whitespace.
    # clean up lines with only whitespace.
    # condense line break streaks of 3 or more.
    md = re.sub(r'\n([\s\*_]+)\n', '\n\n', md)
    md = re.sub(r'\n{3,}', '\n\n', md)

    return md


def clean_highlighted_code(html):
    """strip html from syntax-highlighted
    code (pre and code tags)
    """
    cleaner = clean.Cleaner(allow_tags=['pre'], remove_unknown_tags=False)
    for el in html.findall('.//pre'):
        p = el.getparent()
        cleaned = cleaner.clean_html(el)
        p.replace(el, cleaned)


def convert_span(span):
    """converts spans which specify
    a bold or italic style into
    strong and em tags, respectively
    (nesting them if both are specified).
    """
    p = span.getparent()

    style = span.get('style')
    if style is None:
        return

    builders = []
    if 'bold' in style:
        builders.append(builder.STRONG)
    if 'italic' in style:
        builders.append(builder.EM)

    if builders:
        children = []
        if span.text is not None:
            children.append(span.text)
        for c in span.getchildren():
            children.append(c)
            if c.tail is not None and c.tail.strip():
                # Have to wrap the tail text in a span tag,
                # or else it won't get added.
                children.append(builder.SPAN(c.tail))

        # Recursively apply the builders.
        el = builders[0](*children)
        for b in builders[1:]:
            el = b(el)

        # Replace the old element with the new one.
        p.replace(span, el)
