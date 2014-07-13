# -*- coding: utf-8 -*-
from jinja2 import nodes
from jinja2.ext import Extension
import re


class Spaceless(Extension):
    """
    http://stackoverflow.com/questions/5191147/spaceless-tag-for-jinja-templates

    Removes whitespace between HTML tags at compile time, including tab and newline characters.
    It does not remove whitespace between jinja2 tags or variables. Neither does it remove whitespace between tags
    and their text content.
    Adapted from coffin:
        https://github.com/coffin/coffin/blob/master/coffin/template/defaulttags.py
    """

    tags = set(['spaceless'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endspaceless'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('_strip_spaces', [], [], None, None),
            [], [], body,
        ).set_lineno(lineno)

    def _strip_spaces(self, caller=None):
        regex = re.compile(r'>\s+<', re.DOTALL)
        return regex.sub('><', caller().strip())