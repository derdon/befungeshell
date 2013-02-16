from __future__ import with_statement
from operator import add, sub, mul, floordiv, mod, gt as greater

from befunge_shell import Stack, BefungeShell

from mock import Mock
import pytest


def pytest_generate_tests(metafunc):
    help_messages = dict([
        ('show_stack', 'print the content of the stack'),
        ('show_pc', 'print the direction of the PC (Program Counter)'),
        ('EOF', 'exit the shell with the command "exit", "quit", or by typing '
            'Ctrl+D'),
        ('0', 'Push the number 0 on the stack'),
        ('1', 'Push the number 1 on the stack'),
        ('2', 'Push the number 2 on the stack'),
        ('3', 'Push the number 3 on the stack'),
        ('4', 'Push the number 4 on the stack'),
        ('5', 'Push the number 5 on the stack'),
        ('6', 'Push the number 6 on the stack'),
        ('7', 'Push the number 7 on the stack'),
        ('8', 'Push the number 8 on the stack'),
        ('9', 'Push the number 9 on the stack'),
        ('+', 'Addition: Pop a and b, then push a+b'),
        ('-', 'Subtraction: Pop a and b, then push b-a'),
        ('*', 'Multiplication: Pop a and b, then push a*b'),
        ('/', 'Integer division: Pop a and b, then push b/a, rounded down. '
             'If a is zero, ask the user what result they want.'),
        ('%', 'Modulo: Pop a and b, then push the remainder of the integer '
             'division of b/a. If a is zero, ask the user what result they '
             'want.'),
        ('!', 'Logical NOT: Pop a value. If the value is zero, push 1; '
             'otherwise, push zero.'),
        ('`', 'Greater than: Pop a and b, then push 1 if b>a, otherwise)'
            ' zero.'),
        ('>', 'Change PC (Program Counter) to the direction "right"'),
        ('<', 'Change PC (Program Counter) to the direction "left"'),
        ('^', 'Change PC (Program Counter) to the direction "up"'),
        ('v', 'Change PC (Program Counter) to the direction "down"'),
        ('?', 'Set PC (Program Counter) to a random direction (that means, the'
             ' direction can be the same after this command!)'),
        ('_', 'Pop a value; set PC direction to right if value equals 0, left '
             'otherwise'),
        ('|', 'Pop a value; set PC direction to down if value equals 0, up '
             'otherwise'),
        ('"', 'Start string mode: push each character\'s ASCII value all the'
             ' way up to the next "'),
        (':', 'Duplicate value on top of the stack'),
        ('\\', 'Swap two values on top of the stack'),
        ('$', 'Pop value from the stack'),
        ('.', 'Pop value and output as an integer'),
        (',', 'Pop value and output as ASCII character'),
        ('#', 'Skip the following command'),
        ('&', 'Ask user for a number and push it'),
        ('~', 'Ask user for a character and push its ASCII value'),
        ('@', 'End program')])
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
    elif func_name == 'test_befunge_cmd_help':
        for command, help_message in help_messages.items():
            metafunc.addcall(
                funcargs=dict(cmd=command, expected_help=help_message))
    elif func_name == 'test_fixed_pc':
        for fixed_pc in '><^v':
            metafunc.addcall(funcargs=dict(pc=fixed_pc))
    elif func_name == 'test_convert_to_integer':
        for num_str, expected_num in {'-1': -1, '+0': 0, '3': 3}.items():
            metafunc.addcall(funcargs=dict(
                num_string=num_str, expected_number=expected_num))


@pytest.fixture
def empty_stack():
    return Stack()


@pytest.fixture
def nonempty_stack():
    return Stack([1, 2, 3])


@pytest.fixture
def shell(request):
    monkeypatch = request.getfuncargvalue('monkeypatch')
    monkeypatch.setattr(BefungeShell, 'print_', Mock())
    stdout = Mock(spec=['write', 'flush'], name='stdout')
    stdin = Mock(spec=['readline'], name='stdin')
    return BefungeShell(stdin=stdin, stdout=stdout)


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


def test_input(shell):
    shell.stdin.readline = Mock(return_value='42\n')
    ret = shell.input('age?')
    shell.print_.assert_called_with('age?', False)
    assert ret == '42'


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


def test_befunge_cmd_help(shell, cmd, expected_help):
    shell.do_help(cmd)
    shell.print_.assert_called_with(expected_help)


def test_help_message(shell):
    shell.help_help()
    shell.print_.assert_called_with(
        'Use the command "help" to get a list of all available commands. '
        'Or type "help <command>" to get specific help about this command.')


def test_invalid_pc(shell):
    with pytest.raises(ValueError):
        shell.change_pc('x')


def test_fixed_pc(shell, pc):
    shell.change_pc(pc)
    assert shell.pc == pc


def test_conditional_pc_up(shell):
    shell.stack = Stack([True])
    shell.change_pc('|')
    assert shell.pc == '^'


def test_conditional_pc_down(shell):
    shell.stack = Stack([False])
    shell.change_pc('|')
    assert shell.pc == 'v'


def test_conditional_pc_left(shell):
    shell.stack = Stack([True])
    shell.change_pc('_')
    assert shell.pc == '<'


def test_conditional_pc_right(shell):
    shell.stack = Stack([False])
    shell.change_pc('_')
    assert shell.pc == '>'


def test_exit_simulation(shell):
    shell.simulate_exit()
    shell.print_.assert_called_with('Imagine your script would end now ;-)')


def test_convert_to_integer(shell, num_string, expected_number):
    number = shell.convert_to_integer(num_string)
    assert number == expected_number


def test_convert_invalid_integer(shell):
    ret = shell.convert_to_integer('3.4')
    shell.print_.assert_called_with(
        'Error: You should have entered an integer!')
    assert ret is None
