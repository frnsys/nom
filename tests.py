import unittest
from nom import html2md
from lxml.html import fromstring, tostring

html = '''
    <p>
        <span style='font-weight:bold;font-style:italic;'>
            foobar
            <span style='font-style:italic'>
                lala
                <span style='font-weight:bold;'>
                    yum
                </span>
            </span>
            hey hey
            <span style='font-weight:bold'>
                uh oh
            </span>
            yes
        </span>
    </p>
'''

class html2mdTest(unittest.TestCase):
    def test_html_to_markdown(self):
        markdown = html2md.html_to_markdown(html)
        expected = '_** foobar _ lala ** yum **_ hey hey ** uh oh ** yes **_\n'
        print(markdown)
        self.assertEqual(markdown, expected)

    def test_convert_spans(self):
        expected = '''
            <p>
                <em><strong>
                    foobar
                    <em>
                        lala
                        <strong>
                            yum
                        </strong>
                    </em>
                    <span>
                        hey hey
                    </span>
                    <strong>
                        uh oh
                    </strong>
                    <span>
                        yes
                    </span>
                </strong></em>
            </p>
        '''

        h = fromstring(html)
        for span in h.findall('.//span'):
            html2md.convert_span(span)
        result = tostring(h).decode('utf-8')

        results = [x.replace('\n', '').replace(' ', '') for x in [result, expected]]
        print('=========')
        print(results[0])
        print('=========')
        print(results[1])
        self.assertEqual(results[0], results[1])

