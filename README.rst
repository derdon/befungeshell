befungeshell
============

Description and Usage
---------------------
befungeshell is a little tool which helps you with developping befunge scripts.
After having installed it, you can run befungeshell.py from your terminal to
start it. Here is an example session to illustrate its usage::

    >>> show_stack
    []
    >>> 5
    >>> 5
    >>> *
    >>> 3
    >>> *
    >>> 5
    >>> 2
    >>> *
    >>> show_stack
    [75, 10]
    >>> 2
    >>> *
    >>> show_stack
    [75, 20]
    >>> +
    >>> 2
    >>> +
    >>> show_stack
    [97]
    >>> help
    List of all available commands (type "help <command>")
    ======================================================
    
    Befunge Commands
    ----------------
    0  2  4  6  8  +  *  %  `  <  v  _  "  \  .  #  ~
    1  3  5  7  9  -  /  !  >  ^  ?  |  :  $  ,  &  @
    
    Additional helper functions
    ----------------------------
    show_stack  show_pc  quit  help
    
    >>> help ,
    Pop value and output as ASCII character
    >>> ,
    a
    >>> help show_stack
    print the content of the stack
    >>> show_stack
    []

How to install
--------------
If you use pip_ or easy_install_ to install python packages, enter ``pip
install befungeshell`` or ``easy_install befungeshell``, respectively.

If you have downloaded befungeshell in any way, you can install it by calling
``python setup.py install`` from your terminal inside the befungeshell
directory.

.. _pip: http://www.pip-installer.org/en/latest/index.html
.. _easy_install: http://packages.python.org/distribute/easy_install.html
