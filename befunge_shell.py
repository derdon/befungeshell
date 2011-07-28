#!/usr/bin/env python
# befungeshell - an interactive shell to help writing befunge programs
# Copyright (C) 2011 Simon Liedtke
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import random
from cmd import Cmd
from operator import add, sub, mul, floordiv, mod, not_, gt as greater
try:
    from itertools import izip as zip
except ImportError:  # python3
    pass

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

try:
    range = xrange
except NameError:  # python3
    pass


class Stack(list):
    def pop_exceptionless(self):
        '''Pop the top value of the stack without returning the value. Print a
        warning if the stack was empty.

        '''
        return 0 if not self else self.pop()

    def duplicate_top(self):
        'push the top value to the stack'
        try:
            top_value = self[-1]
        except IndexError:
            top_value = 0
        self.append(top_value)

    def swap_topmost_values(self):
        'swap the two topmost values in the stack'
        self.append(self.pop(-2))


class BefungeShell(Cmd):
    _number_helpers = []
    for i in range(10):
        _number_helpers.append(
            (str(i), 'Push the number %d on the stack' % i)
        )
    misc_helpers = [
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
        ('@', 'End program')
    ]
    _befunge_help = OrderedDict(_number_helpers + misc_helpers)
    _befunge_cmds = _befunge_help.keys()
    doc_header = 'List of all available commands (type "help <command>")'

    def __init__(self, subruler='-', completekey='tab', stdin=None, stdout=None):
        Cmd.__init__(self, completekey, stdin, stdout)
        self.subruler = subruler
        self.prompt = '>>> '
        self.stack = Stack()
        self.string_mode = False
        self.pc = '>'

    def input(self, prompt):
        self.print_(prompt, False)
        input = self.stdin.readline()
        return input.rstrip()

    def print_(self, s='', add_newline=True):
        self.stdout.write('%s%s' % (s, '\n' if add_newline else ''))
        self.stdout.flush()

    def emptyline(self):
        '''do not repeat the last command when simply entering an empty string.
        Instead, do nothing.'''

    # the following method is copied from the stdlib and partially modified
    # (I commented out the lines I dislike) -> allows me to have the commands
    # "help" and "?" to be independent from each other
    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()
        if not line:
            return None, None, line
        #elif line[0] == '?':
        #    line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def default(self, line):
        # check if string mode is enabled; if it is, push the ASCII value
        # of the entered character to the stack
        if self.string_mode:
            # make sure that no double quote is added:
            if not line == '"':
                self.stack.append(ord(line))
            else:
                self.toggle_string_mode()
        else:
            try:
                num = int(line)
            except ValueError:
                # try all the other existing commands
                self.parse_command(line)
            else:
                # converting to number worked, push its value to the stack if
                # it is in the range 0..9
                if num in range(10):
                    self.stack.append(num)
                else:
                    self.print_('Error: only numbers from 0 to 9 are allowed')

    def parse_command(self, command):
        operator = {
            '+': add,
            '-': sub,
            '*': mul,
            '/': floordiv,
            '%': mod,
            '`': greater
        }.get(command)
        if operator is not None:
            self.calculate(operator)
        else:
            if command in ('><^v?_|'):
                # change the direction of the PC (Programm counter)
                self.change_pc(command)
            else:
                func = {
                    '!': self.not_,
                    '"': self.toggle_string_mode,
                    ':': self.stack.duplicate_top,
                    '\\': self.stack.swap_topmost_values,
                    '$': self.stack.pop_exceptionless,
                    '.': lambda: self.print_(self.stack.pop_exceptionless()),
                    ',': lambda: self.print_(
                        chr(self.stack.pop_exceptionless())),
                    '&': lambda: self.stack.append(self.prompt_num()),
                    '~': lambda: self.stack.append(ord(self.prompt_char())),
                    '@': self.simulate_exit
                }.get(command)
                if func is not None:
                    func()
                elif command in '#gp':
                    self.print_(
                        'Note: The commands #, g, p are not supported.')
                else:
                    self.print_('Error: unknown command %r' % command)

    def do_help(self, arg):
        if arg:
            if arg in self._befunge_cmds:
                self.print_(self._befunge_help[arg])
            else:
                docstring = getattr(self, 'do_' + arg).__doc__
                if docstring:
                    self.print_(docstring)
        else:
            header_len = len(self.doc_header)
            self.print_(self.doc_header)
            if self.ruler:
                self.print_(self.ruler * header_len + '\n')
            subheaders = ['Befunge Commands', '\nAdditional helper functions']
            helper_functions = ['show_stack', 'show_pc', 'quit', 'help']
            commands = (self._befunge_cmds, helper_functions)
            for subh, command in zip(subheaders, commands):
                self.print_(subh)
                if self.subruler:
                    self.print_(self.subruler * len(subh))
                self.columnize(command, header_len)
            self.print_()

    def help_help(self):
        self.print_(
            'Use the command "help" to get a list of all available commands. '
            'Or type "help <command>" to get specific help about this command.')

    def calculate(self, operator):
        if len(self.stack) >= 2:
            first = self.stack.pop()
            second = self.stack.pop()
            self.stack.append(int(operator(second, first)))

    def change_pc(self, pc):
        fixed_directions = '><^v'
        if pc in fixed_directions:
            self.pc = pc
        elif pc == '?':
            # choose random direction
            self.pc = random.choice(fixed_directions)
        elif pc in '_|':
            top_val = self.stack.pop_exceptionless()
            self.pc = '><'[bool(top_val)] if pc == '_' else 'v^'[bool(top_val)]
        else:
            raise ValueError(
                'PC (Program Counter) must be either <, >, ^, v, ?, _ or |')

    def toggle_string_mode(self):
        '''one double quote toggles string mode which causes every following
        chracter to be pushed to the stack until the second double quote occurs

        '''
        self.string_mode = not self.string_mode

    def not_(self):
        self.stack.append(int(not_(self.stack.pop_exceptionless())))

    def simulate_exit(self):
        self.print_('Imagine your script would end now ;-)')

    def convert_to_integer(self, s):
        try:
            number = int(s)
        except ValueError:
            self.print_('Error: You should have entered an integer!')
        else:
            return number

    def prompt_num(self):
        return self.convert_to_integer(self.input('Enter a number please: '))

    def prompt_char(self):
        try:
            char = self.input('Enter one character please: ')[:1] or '\n'
        except IndexError:
            self.print_('Error: You should have entered one character!')
        else:
            return char

    def do_show_stack(self, _):
        'print the content of the stack'
        self.print_(repr(self.stack))

    def do_show_pc(self, _):
        'print the direction of the PC (Program Counter)'
        self.print_(repr(self.pc))

    def do_EOF(self, _):
        'exit the shell with the command "exit", "quit", or by typing Ctrl+D'
        return True
    do_exit = do_quit = do_EOF

if __name__ == '__main__':
    shell = BefungeShell()
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        pass
