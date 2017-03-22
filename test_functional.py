from unittest import TestCase

from interactive_cmd import InteractiveCommand


class BashTests(TestCase):
    def setUp(self):
        self.ic = InteractiveCommand('bash')
        self.ic.start()

    def tearDown(self):
        self.ic.kill()

    def test_echo_smoke(self):
        self.ic.writeline('echo foo')
        match = self.ic.wait_until_matched(r'foo', timeout=1)
        self.assertEqual(match.group(), 'foo')

    def test_echo_fail(self):
        self.ic.writeline('echo bar')
        self.assertIsNone(self.ic.wait_until_matched(r'foo', timeout=0.1))

    def test_echo_delayed(self):
        self.ic.writeline('echo bar; sleep 1; echo foo')
        match = self.ic.wait_until_matched(r'foo', timeout=2)
        self.assertEqual(match.group(), 'foo')

    def test_echo_delayed_fail(self):
        self.ic.writeline('echo bar; sleep 1; echo foo')
        self.assertIsNone(self.ic.wait_until_matched(r'foo', timeout=0.5))

    def test_echo_after_exit_raises(self):
        self.ic.writeline('exit')
        with self.assertRaises(BrokenPipeError):
            self.ic.writeline('echo hello')
        self.assertTrue(self.ic.is_running)

    def test_echo_to_closed_stdin_raises(self):
        with self.assertRaises(BrokenPipeError):
            self.ic.writeline('exec 0<&-')
            self.ic.writeline('echo hello')

    def test_write_repeated_smoke(self):
        self.ic.writeline('true')  # make sure $? is 0
        match = self.ic.write_repeated(
            command='test $? -eq 1 && echo "yay"',
            pattern='yay', attempts=3, timeout=0.1)
        self.assertEqual(match.group(), 'yay')
