"""Configuration file for the Sphinx documentation builder."""

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# To generate rst files: sphinx-apidoc -o ./rst ../
# https://stackoverflow.com/questions/2701998/automatically-document-all-modules-recursively-with-sphinx-autodoc
import os
import sys


sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "Python script voor RWS rapportage protocol deel C - technische documentatie"
copyright = "2023, J. Haringa & M. Japink"
author = "J. Haringa & M. Japink"
latex_logo = "./logo_we_rws.png"

# The full version, including alpha/beta/rc tags
release = "1.0.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
]

extensions.append("sphinx.ext.intersphinx")
extensions.append("sphinx.ext.mathjax")
extensions.append("sphinx.ext.graphviz")
extensions.append("sphinx.ext.coverage")
extensions.append("sphinx.ext.napoleon")

exclude_patterns = "*.txt"
autoclass_content = "both"
html_show_sourcelink = False
autodoc_inherit_docstrings = True
set_type_checking_flag = True
# autodoc_default_flags = ["members"]
autosummary_generate = True


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build"]  # type: ignore

latex_engine = "pdflatex"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
