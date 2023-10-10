#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# function-pipe documentation build configuration file, created by
# sphinx-quickstart on Fri Jan  6 16:49:22 2017.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import datetime
import os

import typing_extensions as tp

import static_frame as sf
from static_frame.core.interface import DOCUMENTED_COMPONENTS
from static_frame.core.interface import INTERFACE_GROUP_DOC
from static_frame.core.interface import INTERFACE_GROUP_ORDER
from static_frame.core.interface import InterfaceSummary

PREFIX_START = '#start_'
PREFIX_END = '#end_'

def get_defined() -> tp.Set[str]:

    source_dir = os.path.abspath(os.path.dirname(__file__))
    fp = os.path.join(source_dir, 'examples.txt')

    defined = set()
    signature_start = ''
    signature_end = ''

    with open(fp) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith(PREFIX_START):
                signature_start = line.replace(PREFIX_START, '').strip()
            elif line.startswith(PREFIX_END):
                signature_end = line.replace(PREFIX_END, '').strip()
                if signature_start == signature_end:
                    if signature_start in defined:
                        raise RuntimeError(f'duplicate definition: {signature_start}')
                    defined.add(signature_start)
                    signature_start = ''
                    signature_end = ''
                else:
                    raise RuntimeError(f'mismatched: {signature_start}: {signature_end}')
    return defined


def get_jinja_contexts() -> tp.Dict[str, tp.Any]:
    print('calling get_jinja_contexts')
    # NOTE: we build dictionaries here so that we can pre-select groups when setting up args into the jina tempalates in source_build.py

    post: tp.Dict[str, tp.Any] = {}

    # for docs
    post['examples_defined'] = get_defined()
    post['interface_group_doc'] = INTERFACE_GROUP_DOC
    post['toc'] = {}
    post['interface'] = {}
    for cls in DOCUMENTED_COMPONENTS:
        inter = InterfaceSummary.to_frame(cls,
                minimized=False,
                max_args=99, # +inf, but keep as int
                )
        post['interface'][cls.__name__] = {}

        groups = []
        for ig in INTERFACE_GROUP_ORDER:
            ig_tag = ig.replace('-', '_').replace(' ', '_').lower()
            inter_sub = inter.loc[inter['group'] == ig]
            if len(inter_sub) == 0: # skip empty groups
                continue
            post['interface'][cls.__name__][ig_tag] = (
                    cls.__name__,
                    ig,
                    ig_tag,
                    inter_sub,
                    )
            groups.append((ig, ig_tag))

        post['toc'][cls.__name__] = tuple(groups)

    return post

# NOTE: this incurs processing on module load
jinja_contexts = {'ctx': get_jinja_contexts()}


# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.viewcode',
        'sphinx.ext.napoleon',
        'sphinx.ext.graphviz',
        'sphinx.ext.inheritance_diagram',
        # 'sphinxcontrib.napoleon',
        'sphinx_jinja',
        ]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'StaticFrame'
copyright = '%s, Christopher Ariza' % datetime.datetime.now().year

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '.'.join(sf.__version__.split('.')[:2])
# The full version, including alpha/beta/rc tags.
release = sf.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns: tp.List[str] = []

add_module_names = False
# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# on_rtd = os.environ.get('READTHEDOCS') == 'True'
# if on_rtd:
#     html_theme = 'default'
# else:
#     import sphinx_rtd_theme
#     html_theme = 'sphinx_rtd_theme'
#     html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_theme_options = {
    'logo_only': True,
    'display_version': False,
    'prev_next_buttons_location': 'both',
    'style_nav_header_background': '#343131',
    'collapse_navigation': True,
    'sticky_navigation': False,
    'navigation_depth': 4,
    'includehidden': False,
    'titles_only': False
}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '../images/sf-logo-web_icon-small.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = '../images/favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'static-frame'


# -- Options for LaTeX output --------------------------------------------------

latex_elements: tp.Dict[str, str] = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
# latex_documents = []

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages: tp.List[tp.Tuple[str, str, str, str, str]] = []

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents: tp.List[tp.Tuple[str, str, str, str, str, str, str]] = []

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False


autodoc_typehints = 'none'