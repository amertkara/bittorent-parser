#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_btparser
----------------------------------

Tests for `btparser` module.
"""

import unittest
import os

from btparser.btparser import BTParser


class TestBtparser(unittest.TestCase):

    def test_ubuntu(self):
        parser = BTParser(os.path.join(os.path.dirname(__file__), "ubuntu-12.04.4-desktop-amd64.iso.torrent"))
        parser.get_content()

        self.assertEqual(parser.metadata.get("announce"), "http://torrent.ubuntu.com:6969/announce")

    def test_exceptions(self):
        # Torrent content is not a dictionary
        parser = BTParser("", "asde")
        self.assertRaises(SyntaxError, parser.get_content)

        # Integer is not an actual integer, int's ValueError is handled heres
        parser = BTParser("", "d4:key1inotanumberee")
        self.assertRaises(SyntaxError, parser.get_content)

        # List is not formatted properly
        parser = BTParser("", "dli4ee")
        self.assertRaises(SyntaxError, parser.get_content)


if __name__ == '__main__':
    unittest.main()