# Copyright (c) 2020-2021 Jan Lana
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import re
import lxml.etree


def tex_escape(text):
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)


ns = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0',
      'xlink': 'http://www.w3.org/1999/xlink'}

hdr = """
\\documentclass[9pt]{extarticle}
\\usepackage{luatextra,fontspec,polyglossia,microtype}
\\setmainlanguage{czech}
\\setmainfont{Open Sans}

\\usepackage[paperheight=122mm,paperwidth=91mm,margin=3mm,footskip=3mm,includefoot]{geometry}


\\usepackage{fancyhdr,lastpage}
\\pagestyle{fancy}
\\fancyhead{}
\\cfoot{\\thepage/\\pageref{LastPage}}
\\renewcommand{\\headrulewidth}{0pt}
\\pagestyle{fancy}


\\begin{document}
"""

notes = None


def parse_p(el):
    if el.text:
        print(el.text, end="")

    for item in el.getchildren():
        tag = lxml.etree.QName(item).localname
        if tag == 'a':
            href = item.get(f"{{{ns['xlink']}}}href")
            note = notes[0].xpath(f'//fb:section[@id="{href[1:]}"]/fb:p/child::text()', namespaces=ns)
            print(f"\\footnote{{{tex_escape((' '.join(note)).strip())}}}", end="")
        if item.tail:
            print(item.tail, end="")

    print("\n")


def parse_section(el, deep):
    titles = el.xpath('fb:title', namespaces=ns)

    if titles:
        if deep == 0:
            print("\\section*{", end='')
        elif deep == 1:
            print("\\subsection*{", end='')
        else:
            print("\\subsubsection*{", end='')

        for t in titles:
            print(tex_escape(t.getchildren()[0].text.strip()), end='')

        print("}")
    else:
        print("\\bigskip")

    for s in el.getchildren():
        tag = lxml.etree.QName(s).localname
        if tag == 'section':
            parse_section(s, deep+1)
        elif tag == 'p':
            parse_p(s)
        elif tag == 'empty-line':
            print("\\medskip")
        else:
            continue


def fb2latex(src):
    global notes

    tree = lxml.etree.parse(src)
    root = tree.getroot()

    body = root.xpath('fb:body', namespaces=ns)[0]
    notes = root.xpath('fb:body[@name="notes"]', namespaces=ns)

    print(hdr)
    for s in body.getchildren():
        tag = lxml.etree.QName(s).localname
        if tag == 'section':
            parse_section(s, 0)
        else:
            raise Exception(s)
    print("\\end{document}")


def main():
    parser = argparse.ArgumentParser(description='Convert fb2 to latex')
    parser.add_argument('src', type=argparse.FileType('r'))
    args = parser.parse_args()

    fb2latex(args.src)


if __name__ == "__main__":
    main()