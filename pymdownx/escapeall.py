"""
EscapeAll.

pymdownx.escapeall
Escape everything.

MIT license.

Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import Pattern, SubstituteTagPattern
from markdown.postprocessors import Postprocessor
from markdown import util as md_util
import re
from . import util

ESCAPE_RE = r'\\(.)'
ESCAPE_NO_NL_RE = r'\\([^\n])'
HARDBREAK_RE = r'\\\n'
UNESCAPE_PATTERN = re.compile('%s(\d+)%s' % (md_util.STX, md_util.ETX))


class EscapeAllPattern(Pattern):
    """Return an escaped character."""

    def __init__(self, pattern, nbsp):
        """Initialize."""

        self.nbsp = nbsp
        Pattern.__init__(self, pattern)

    def handleMatch(self, m):
        """Convert the char to an escaped character."""

        char = m.group(2)
        if self.nbsp and char == ' ':
            escape = md_util.AMP_SUBSTITUTE + 'nbsp;'
        else:
            escape = '%s%s%s' % (md_util.STX, util.get_ord(char), md_util.ETX)
        return escape


class EscapeAllPostprocessor(Postprocessor):
    """Post processor to strip out unwanted content."""

    def unescape(self, m):
        """Unescape the escaped chars."""

        return util.get_char(int(m.group(1)))

    def run(self, text):
        """Search document for esaped chars."""

        return UNESCAPE_PATTERN.sub(self.unescape, text)


class EscapeAllExtension(Extension):
    """Extension that allows you to escape everything."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'hardbreak': [
                False,
                "Turn escaped newlines to hardbreaks - Default: False"
            ],
            'nbsp': [
                False,
                "Turn escaped spaces to non-breaking spaces - Default: False"
            ]
        }
        super(EscapeAllExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Escape all."""

        self.md = md
        config = self.getConfigs()
        hardbreak = config['hardbreak']
        md.inlinePatterns['escape'] = EscapeAllPattern(
            ESCAPE_NO_NL_RE if hardbreak else ESCAPE_RE, config['nbsp']
        )
        md.postprocessors['unescape'] = EscapeAllPostprocessor(md)
        if config['hardbreak']:
            try:
                md.inlinePatterns.add("hardbreak", SubstituteTagPattern(HARDBREAK_RE, 'br'), "<nl")
            except Exception:
                md.inlinePatterns.add("hardbreak", SubstituteTagPattern(HARDBREAK_RE, 'br'), "_end")


def makeExtension(*args, **kwargs):
    """Return extension."""

    return EscapeAllExtension(*args, **kwargs)