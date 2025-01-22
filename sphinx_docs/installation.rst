Installation
==================

Installation of Programs
~~~~~~~~~~~~~~~~~~~~~~~~~

The script has been tested on Windows 11 and WSL2-Ubuntu. To ensure proper functionality, at least Python and Poetry need to be installed. The following installations need to be performed on the system only once.

Pyenv - Optional
----------------

Install pyenv if you require multiple Python versions on your system. Pyenv can assist you with this: `pyenv-win repository <https://github.com/pyenv-win/pyenv-win>`_. Pay attention to the installation of certain system variables.

Python
------

The script was developed and tested in Python 3.12. Install:

- `Python 3.12 <https://www.python.org/downloads>`_

or

- Using pyenv via the command line:

  .. code-block:: cmd

    pyenv install 3.12.1
    pyenv global 3.12.1

Poetry
------

The script depends on several packages. At the time of writing, Poetry is considered the best package manager. See `Poetry documentation <https://python-poetry.org/docs/>`_. Pay attention to the installation of certain system variables. Test the Poetry installation from the command line:

.. code-block:: cmd

    poetry --version

Git - Optional
--------------

The script is hosted and managed on Gitlab. Git can be used to synchronize directly with the repository. Installation and configuration settings are described in "Installing Git" and "First-time git setup" at the following links:

- `Git Book (English) <https://git-scm.com/book/en/v2>`_
- `Git Book (Dutch) <https://git-scm.com/book/nl/v2>`_

Code Editor / IDE
-----------------

While the script can be started from the command line, it is more convenient to use an Integrated Development Environment (IDE) or code editor. There are many code editors available, and it doesn't matter which one you use, as long as it supports Python. Python is provided with IDLE by default, which is a good option. However, we recommend using Thonny as a simple alternative. See `Thonny documentation <https://realpython.com/python-thonny/>`_.


