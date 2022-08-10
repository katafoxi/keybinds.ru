from django.test import TestCase
from keymap.parser_pycharm import pycharm_parser_settings_file, get_modifiers_code_with_key


class ParserTest(TestCase):

    def test_parse_settings_file(self):
        with open(r'tests/test.xml') as xml_file:
            test_file = xml_file
            parse = pycharm_parser_settings_file(test_file)
        self.assertEqual(parse, {'$Redo': {'z': 'cs', 'back_space': 'as'}})

    def test_get_modifiers_code_with_key(self):
        self.assertEqual(get_modifiers_code_with_key("shift ctrl z"), {"z": "cs"})
        self.assertEqual(get_modifiers_code_with_key("z"), {'z': 'push'})