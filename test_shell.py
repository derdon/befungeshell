from __future__ import with_statement
from operator import add, sub, mul, floordiv, mod, gt as greater

from befunge_shell import Stack, BefungeShell

from mock import Mock
import pytest


def pytest_generate_tests(metafunc):
    operators = {
        '+': add,
        '-': sub,
        '*': mul,
        '/': floordiv,
        '%': mod,
        '`': greater
    }
    change_pc_commands = '><^v?_|'
    unsupported_commands = '#gp'
    func_name = metafunc.function.__name__
    if func_name == 'test_shell_calc_op':
        for command, op_func in operators.items():
            metafunc.addcall(funcargs=dict(cmd=command, callback=op_func))
    elif func_name == 'test_parse_change_pc_command':
        for command in change_pc_commands:
            metafunc.addcall(funcargs=dict(cmd=command))
    elif func_name == 'test_unsupported_commands':
        for command in unsupported_commands:
            metafunc.addcall(funcargs=dict(unsupported_cmd=command))


def pytest_funcarg__empty_stack(request):
    return Stack()


def pytest_funcarg__nonempty_stack(request):
    return Stack([1, 2, 3])


def pytest_funcarg__shell(request):
    monkeypatch = request.getfuncargvalue('monkeypatch')
    monkeypatch.setattr(BefungeShell, 'print_', Mock())
    stdout = Mock(spec=['write', 'flush'], name='stdout')
    return BefungeShell(stdin=Mock(name='stdin'), stdout=stdout)


class TestStackPop(object):
    def test_empty(self, empty_stack):
        assert empty_stack.pop_exceptionless() == 0

    def test_nonempty(self, nonempty_stack):
        item = nonempty_stack.pop_exceptionless()
        assert item == 3


class TestStackDuplicateTop(object):
    def test_empty(self, empty_stack):
        assert len(empty_stack) == 0
        empty_stack.duplicate_top()
        assert len(empty_stack) == 1
        assert empty_stack == Stack([0])

    def test_nonempty(self, nonempty_stack):
        nonempty_stack.duplicate_top()
        assert nonempty_stack == Stack([1, 2, 3, 3])


class TestStackSwap(object):
    def test_empty(self, empty_stack):
        with pytest.raises(IndexError):
            empty_stack.swap_topmost_values()

    def test_nonempty(self, nonempty_stack):
        nonempty_stack.swap_topmost_values()
        assert nonempty_stack == Stack([1, 3, 2])


def test_shell_init():
    shell = BefungeShell()
    assert shell.subruler == '-'
    assert shell.completekey == 'tab'
    assert shell.prompt == '>>> '
    assert shell.stack == Stack()
    assert shell.string_mode == False
    assert shell.pc == '>'


class TestStringMode(object):
    def test_non_double_quote(self, shell):
        shell.string_mode = True
        shell.default('a')
        assert shell.stack == Stack([97])

    def test_double_quote(self, shell):
        shell.string_mode = True
        shell.default('"')
        assert shell.string_mode == False


class TestIntegers(object):
    def test_valid_num(self, shell):
        shell.default('5')
        assert shell.stack == Stack([5])

    def test_invalid_num(self, shell):
        shell.default('23')
        shell.print_.assert_called_with(
            'Error: only numbers from 0 to 9 are allowed')


def test_shell_non_integer(monkeypatch):
    monkeypatch.setattr(BefungeShell, 'parse_command', Mock())
    shell = BefungeShell()
    shell.default('foo')
    shell.parse_command.assert_called_with('foo')


def test_shell_calc_op(monkeypatch, cmd, callback):
    monkeypatch.setattr(BefungeShell, 'calculate', Mock())
    shell = BefungeShell()
    shell.parse_command(cmd)
    shell.calculate.assert_called_with(callback)


def test_parse_change_pc_command(monkeypatch, cmd):
    monkeypatch.setattr(BefungeShell, 'change_pc', Mock())
    shell = BefungeShell()
    shell.parse_command(cmd)
    shell.change_pc.assert_called_with(cmd)


def test_unsupported_commands(shell, unsupported_cmd):
    shell.parse_command(unsupported_cmd)
    shell.print_.assert_called_with(
        'Note: The commands #, g, p are not supported.')


def test_unknown_command(shell):
    shell.parse_command('thiscommanddoesnotexistandwillneverbe')
    shell.print_.assert_called_with(
        "Error: unknown command 'thiscommanddoesnotexistandwillneverbe'")


def test_help_message(shell):
    shell.help_help()
    shell.print_.assert_called_with(
        'Use the command "help" to get a list of all available commands. '
        'Or type "help <command>" to get specific help about this command.')


def test_exit_simulation(shell):
    shell.simulate_exit()
    shell.print_.assert_called_with('Imagine your script would end now ;-)')
