Run the main script
====================================


Retrieving the Script
~~~~~~~~~~~~~~~~~~~~~~~~~~

RWS provides the script as a zipfile, or you can download/clone it from the Gitlab repository. It is easiest to place the unzipped script in an easily accessible folder, which saves a lot of typing in the command prompt. For example: C:\scripts\benthos. However, each company may handle this differently from an IT perspective. When in doubt, consult with your IT department.

Installing Packages
~~~~~~~~~~~~~~~~~~~~~~

Navigate in the terminal/prompt to the script folder.

Type the following command on the command line:

.. code-block:: cmd

   poetry install

Poetry creates a virtual environment containing all the packages required by the script. Each time the script needs to be used, the virtual environment must be activated.

Activating the Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Navigate in the terminal/prompt to the script folder.

Type the following command on the command line:

.. code-block:: cmd

   poetry shell

If everything goes well, Poetry responds with the full path to the virtual environment. For example:

.. code-block:: cmd
   
   Spawning shell within C:\Users\Maarten Japink\AppData\Local\pypoetry\Cache\virtualenvs\rws-project-BHTE6_UZ-py3.12
