#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Extract message strings from python modules, page template files
and ZCML files.

"""

import fnmatch
import functools
import getopt
import os
import sys
import time
import tokenize
import traceback
from collections import defaultdict

import zope.cachedescriptors.property
from zope.i18nmessageid import Message
from zope.interface import implementer

from zope.app.locales.interfaces import IPOTEntry
from zope.app.locales.interfaces import IPOTMaker
from zope.app.locales.interfaces import ITokenEater
from zope.app.locales.pygettext import make_escapes
from zope.app.locales.pygettext import normalize
from zope.app.locales.pygettext import safe_eval


DEFAULT_CHARSET = 'UTF-8'
DEFAULT_ENCODING = '8bit'
_import_chickens = {}, {}, ("*",)  # dead chickens needed by __import__

DEFAULT_POT_HEADER = pot_header = '''\
##############################################################################
#
# Copyright (c) 2003-2019 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
msgid ""
msgstr ""
"Project-Id-Version: %(version)s\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: Zope 3 Developers <zope-dev@zope.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=%(charset)s\\n"
"Content-Transfer-Encoding: %(encoding)s\\n"
"Generated-By: zope/app/locales/extract.py\\n"

'''


@implementer(IPOTEntry)
@functools.total_ordering
class POTEntry:
    r"""This class represents a single message entry in the POT file.

    >>> make_escapes(0)
    >>> class FakeFile(object):
    ...     def write(self, data):
    ...         assert isinstance(data, bytes), data
    ...         print(data.decode('utf-8'))

    Let's create a message entry:

    >>> entry = POTEntry(Message("test", default="default"))
    >>> entry.addComment("# Some comment")
    >>> entry.addLocationComment(os.path.join("path", "file"), 10)

    Then we feed it a fake file:

    >>> entry.write(FakeFile())
    # Some comment
    #: path/file:10
    #. Default: "default"
    msgid "test"
    msgstr ""
    <BLANKLINE>

    Multiline default values generate correct comments:

    >>> entry = POTEntry(Message("test", default="\nline1\n\tline2"))
    >>> entry.write(FakeFile())
    #. Default: ""
    #.  "line1\n"
    #.  "\tline2"
    msgid "test"
    msgstr ""
    <BLANKLINE>

    Unicode can be used in msgids and default values:

    >>> entry = POTEntry(Message(u"\u263B", default=u"\u253A"))
    >>> entry.write(FakeFile())
    #. Default: "\342\224\272"
    msgid "\342\230\273"
    msgstr ""
    <BLANKLINE>

    But msgid might be an ascii encoded string and `default` might be a
    (byte) string with the DEFAULT_ENCODING, too:

    >>> entry = POTEntry(Message("Oe", default=b"\xd6"))
    >>> entry.write(FakeFile())
    #. Default: "\326"
    msgid "Oe"
    msgstr ""
    <BLANKLINE>

    Entries are fully ordered by msgid and then locations; comments
    are ignored:

    >>> entry = POTEntry('aaa')
    >>> entry_w_comment = POTEntry('aaa')
    >>> entry_w_comment.addComment('comment')
    >>> entry == entry_w_comment
    True
    >>> entry_w_comment.addLocationComment('zzz', 123)
    >>> entry == entry_w_comment
    False
    >>> entry < entry_w_comment
    True

    Each location is only stored once:

    >>> entry = POTEntry('aaa')
    >>> entry.addLocationComment('zzz', 123)
    >>> entry.addLocationComment('zzz', 123)
    >>> entry.locations
    (('zzz', 123),)

    The cache is cleared on a new entry:

    >>> entry = POTEntry('aaa')
    >>> entry.addLocationComment('zzz', 123)
    >>> entry.addLocationComment('yyy', 456)
    >>> entry.locations
    (('yyy', 456), ('zzz', 123))

    """

    def __init__(self, msgid, comments=None):
        self.msgid = msgid
        self.comments = comments or ''
        self._locations = set()

    @zope.cachedescriptors.property.Lazy
    def locations(self):
        return tuple(sorted(self._locations))

    def addComment(self, comment):
        self.comments += comment + '\n'

    def addLocationComment(self, filename, line):
        filename = filename.replace(os.sep, '/')
        self._locations.add((filename, line))
        try:  # purge the cache.
            del self.locations
        except AttributeError:
            pass

    def write(self, file):
        if self.comments:
            file.write(self.comments.encode(DEFAULT_CHARSET)
                       if not isinstance(self.comments, bytes)
                       else self.comments)
        for filename, line in self.locations:
            file.write(b'#: %s:%d\n' % (filename.encode(DEFAULT_CHARSET),
                                        line))
        if (isinstance(self.msgid, Message) and
                self.msgid.default is not None):
            default = self.msgid.default.strip()

            if not isinstance(default, bytes):
                default = default.encode(DEFAULT_CHARSET)

            lines = normalize(default).split(b"\n")
            lines[0] = b"#. Default: %s\n" % lines[0]
            for i in range(1, len(lines)):
                lines[i] = b"#.  %s\n" % lines[i]
            file.write(b"".join(lines))
        msgid = self.msgid.encode(DEFAULT_CHARSET)
        file.write(b'msgid %s\n' % normalize(msgid))
        file.write(b'msgstr ""\n')
        file.write(b'\n')

    def __eq__(self, other):
        if not isinstance(other, POTEntry):
            return NotImplemented  # pragma: no cover
        return self.locations == other.locations and self.msgid == other.msgid

    def __lt__(self, other):
        if not isinstance(other, POTEntry):
            return NotImplemented  # pragma: no cover
        return ((self.locations, self.msgid) < (other.locations, other.msgid))

    def __repr__(self):
        return '<POTEntry: %r>' % self.msgid


@implementer(IPOTMaker)
class POTMaker:
    """This class inserts sets of strings into a POT file."""

    def __init__(self, output_fn, path, header_template=None):
        self._output_filename = output_fn
        self.path = path
        if header_template is not None:
            if os.path.exists(header_template):
                with open(header_template) as file:
                    self._pot_header = file.read()
            else:
                raise ValueError(
                    "Path {!r} derived from {!r} does not exist.".format(
                        os.path.abspath(header_template), header_template))
        else:
            self._pot_header = DEFAULT_POT_HEADER
        self.catalog = {}

    def add(self, strings, base_dir=None):
        for msgid, locations in strings.items():
            if msgid == '':
                continue
            if msgid not in self.catalog:
                self.catalog[msgid] = POTEntry(msgid)

            for filename, lineno in locations:
                if base_dir:
                    filename = strip_base_dir(filename, base_dir)
                self.catalog[msgid].addLocationComment(filename, lineno)

    def _getProductVersion(self):
        # First, try to get the product version
        fn = os.path.join(self.path, 'version.txt')
        if os.path.exists(fn):
            with open(fn) as f:
                return f.read().strip()
        return "Unknown"

    def write(self):
        with open(self._output_filename, 'wb') as file:
            formatted_header = self._pot_header % {
                'time': time.ctime(),
                'version': self._getProductVersion(),
                'charset': DEFAULT_CHARSET,
                'encoding': DEFAULT_ENCODING}
            file.write(formatted_header.encode(DEFAULT_CHARSET))

            # Sort the catalog entries by filename
            catalog = self.catalog.values()

            # Write each entry to the file
            for entry in sorted(catalog):
                entry.write(file)


@implementer(ITokenEater)
class TokenEater:
    """This is almost 100% taken from `pygettext.py`, except that I
    removed all option handling and output a dictionary.

    >>> eater = TokenEater()
    >>> make_escapes(0)

    TokenEater eats tokens generated by the standard python module
    `tokenize`.

    >>> from io import BytesIO

    We feed it a (fake) file:

    >>> file = BytesIO(
    ...     b"_(u'hello ${name}', u'buenos dias', {'name': 'Bob'}); "
    ...     b"_(u'hi ${name}', mapping={'name': 'Bob'}); "
    ...     b"_('k, bye', ''); "
    ...     b"_('kthxbye')"
    ...     )
    >>> for t in tokenize.tokenize(file.readline):
    ...     eater(*t)

    The catalog of collected message ids contains our example

    >>> catalog = eater.getCatalog()
    >>> items = sorted(catalog.items())
    >>> items
    [(u'hello ${name}', [(None, 1)]),
     (u'hi ${name}', [(None, 1)]),
     (u'k, bye', [(None, 1)]),
     (u'kthxbye', [(None, 1)])]

    The key in the catalog is not a unicode string, it's a real
    message id with a default value:

    >>> msgid = items.pop(0)[0]
    >>> msgid
    u'hello ${name}'
    >>> msgid.default
    u'buenos dias'

    >>> msgid = items.pop(0)[0]
    >>> msgid
    u'hi ${name}'
    >>> msgid.default

    >>> msgid = items.pop(0)[0]
    >>> msgid
    u'k, bye'
    >>> msgid.default
    u''

    >>> msgid = items.pop(0)[0]
    >>> msgid
    u'kthxbye'
    >>> msgid.default

    Note that everything gets converted to unicode.
    """

    def __init__(self):
        self.__messages = {}
        self.__state = self.__waiting
        self.__data = []
        self.__lineno = -1
        self.__freshmodule = 1
        self.__curfile = None

    def __call__(self, ttype, tstring, stup, etup, line):
        self.__state(ttype, tstring, stup[0])

    def __waiting(self, ttype, tstring, lineno):
        if ttype == tokenize.NAME and tstring in ('_',):
            self.__state = self.__keywordseen

    def __keywordseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == '(':
            self.__data = []
            self.__msgid = ''
            self.__default = None
            self.__lineno = lineno
            self.__state = self.__openseen
        else:
            self.__state = self.__waiting

    def __openseen(self, ttype, tstring, lineno):
        if ((ttype == tokenize.OP and tstring == ')') or
                (ttype == tokenize.NAME and tstring == 'mapping')):
            # We've seen the last of the translatable strings.  Record the
            # line number of the first line of the strings and update the list
            # of messages seen.  Reset state for the next batch.  If there
            # were no strings inside _(), then just ignore this entry.
            if self.__data or self.__msgid:
                if self.__default:
                    msgid = self.__msgid
                    default = self.__default
                elif self.__msgid:
                    msgid = self.__msgid
                    if self.__data:
                        default = ''.join(self.__data)
                    else:
                        default = None
                else:
                    msgid = ''.join(self.__data)
                    default = None
                self.__addentry(msgid, default)
            self.__state = self.__waiting
        elif ttype == tokenize.OP and tstring == ',':
            if not self.__msgid:
                self.__msgid = ''.join(self.__data)
            elif not self.__default and self.__data:
                self.__default = ''.join(self.__data)
            self.__data = []
        elif ttype == tokenize.STRING:
            self.__data.append(safe_eval(tstring))

    def __addentry(self, msg, default=None, lineno=None, isdocstring=0):
        if lineno is None:
            lineno = self.__lineno

        if default is not None and not isinstance(default, str):
            default = default.decode(DEFAULT_CHARSET)
        msg = Message(msg, default=default)
        entry = (self.__curfile, lineno)
        self.__messages.setdefault(msg, {})[entry] = isdocstring

    def set_filename(self, filename):
        self.__curfile = filename
        self.__freshmodule = 1

    def getCatalog(self):
        catalog = {}
        # Sort the entries.  First sort each particular entry's keys, then
        # sort all the entries by their first item.
        reverse = defaultdict(list)
        for k, v in self.__messages.items():
            reverse[tuple(sorted(v.keys()))].append((k, v))

        rkeys = reverse.keys()
        for rkey in sorted(rkeys):
            rentries = reverse[rkey]
            rentries.sort()
            for msgid, locations in rentries:
                catalog[msgid] = []

                locations = locations.keys()

                for filename, lineno in sorted(locations):
                    catalog[msgid].append((filename, lineno))

        return catalog


def find_files(dir, pattern, exclude=()):
    files = []

    for dirpath, _dirnames, filenames in os.walk(dir):
        files.extend(
            [os.path.join(dirpath, name)
             for name in fnmatch.filter(filenames, pattern)
             if name not in exclude])

    return files


def relative_path_from_filename(filename, sys_path=None):
    """Translate a filename into a relative path.

    We are using the python path to determine what the shortest relative path
    should be:

       >>> sys_path = ["/src/project/Zope3/src/",
       ...             "/src/project/src/schooltool",
       ...             "/python2.4/site-packages"]

       >>> relative_path_from_filename(
       ...     "/src/project/src/schooltool/module/__init__.py",
       ...     sys_path=sys_path)
       'module/__init__.py'

       >>> relative_path_from_filename(
       ...     "/src/project/src/schooltool/module/file.py",
       ...     sys_path=sys_path)
       'module/file.py'

       >>> relative_path_from_filename(
       ...     "/src/project/Zope3/src/zope/app/locales/extract.py",
       ...     sys_path=sys_path)
       'zope/app/locales/extract.py'

    """
    if sys_path is None:
        sys_path = sys.path

    filename = os.path.abspath(filename)
    common_path_lengths = [
        len(os.path.commonprefix([filename, os.path.abspath(path)]))
        for path in sys_path]
    s = max(common_path_lengths) + 1
    # a path in sys.path ends with a separator
    if filename[s - 2] == os.path.sep:
        s -= 1
    return filename[s:]


def module_from_filename(filename, sys_path=None):
    """Translate a filename into a name of a module.

    We are using the python path to determine what the shortest module
    name should be:

       >>> sys_path = ["/src/project/Zope3/src/",
       ...             "/src/project/src/schooltool",
       ...             "/python2.4/site-packages"]

       >>> module_from_filename(
       ...     "/src/project/src/schooltool/module/__init__.py",
       ...     sys_path=sys_path)
       'module'

       >>> module_from_filename(
       ...     "/src/project/src/schooltool/module/file.py",
       ...     sys_path=sys_path)
       'module.file'

       >>> module_from_filename(
       ...     "/src/project/Zope3/src/zope/app/locales/extract.py",
       ...     sys_path=sys_path)
       'zope.app.locales.extract'

    """
    filename = relative_path_from_filename(filename, sys_path)
    # remove .py ending from filenames
    # replace all path separators with a dot
    # remove the __init__ from the import path
    return filename[:-3].replace(os.path.sep, ".").replace(".__init__", "")


def py_strings(dir, domain="zope", exclude=(), verify_domain=False):
    """Retrieve all Python messages from `dir` that are in the `domain`.

    Retrieves all the messages in all the domains if verify_domain is
    False.
    """
    eater = TokenEater()
    make_escapes(0)
    filenames = find_files(
        dir, '*.py', exclude=('extract.py', 'pygettext.py') + tuple(exclude)
    )
    for filename in filenames:
        if verify_domain:
            module_name = module_from_filename(filename)
            try:
                module = __import__(module_name, *_import_chickens)
            except ImportError:  # pragma: no cover
                # XXX if we can't import it - we assume that the domain is
                # the right one
                print("Could not import %s, "
                      "assuming i18n domain OK" % module_name, file=sys.stderr)
            else:
                mf = getattr(module, '_', None)
                # XXX if _ is has no _domain set we assume that the domain
                # is the right one, so if you are using something non
                # MessageFactory you should set it's _domain attribute.
                if hasattr(mf, '_domain'):
                    if mf._domain != domain:
                        # domain mismatch - skip this file
                        continue
                elif mf:
                    print("Could not figure out the i18n domain"
                          " for module %s, assuming it is OK" % module_name,
                          file=sys.stderr)

        with open(filename, 'rb') as fp:
            eater.set_filename(filename)
            try:
                for t in tokenize.tokenize(fp.readline):
                    eater(*t)
            except tokenize.TokenError as e:  # pragma: no cover
                print('%s: %s, line %d, column %d' % (
                    e[0], filename, e[1][0], e[1][1]), file=sys.stderr)

    return eater.getCatalog()


def _relative_locations(locations):
    """Return `locations` with relative paths.

    locations: list of tuples(path, lineno)
    """
    return [(relative_path_from_filename(path), lineno)
            for path, lineno in locations]


def zcml_strings(dir, domain="zope", site_zcml=None):
    """Retrieve all ZCML messages from `dir` that are in the `domain`."""
    from zope.configuration import config
    from zope.configuration import xmlconfig

    # Load server-independent site config
    context = config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    context.provideFeature("devmode")
    context = xmlconfig.file(site_zcml, context=context, execute=False)

    strings = context.i18n_strings.get(domain, {})
    strings = {key: _relative_locations(value)
               for key, value in strings.items()}
    return strings


def tal_strings(dir,
                domain="zope",
                include_default_domain=False,
                exclude=(),
                filePattern='*.pt'):
    """Retrieve all TAL messages from `dir` that are in the `domain`.

      >>> from zope.app.locales import extract
      >>> import tempfile
      >>> dir = tempfile.mkdtemp()

    Let's create a page template in the i18n domain ``test``:
      >>> with open(os.path.join(dir, 'test.pt'), 'w') as testpt:
      ...    _ = testpt.write(
      ...         '<tal:block i18n:domain="test"'
      ...         ' i18n:translate="">test</tal:block>')

    And now one in no domain:
      >>> with open(os.path.join(dir, 'no.pt'), 'w') as nopt:
      ...    _ = nopt.write(
      ...         '<tal:block i18n:translate="">no domain</tal:block>')

    Now let's find the strings for the domain ``test``:

      >>> strs = extract.tal_strings(
      ...     dir, domain='test', include_default_domain=True)
      >>> len(strs)
      2
      >>> strs[u'test']
      [('...test.pt', 1)]
      >>> strs[u'no domain']
      [('...no.pt', 1)]

    And now an xml file
      >>> with open(os.path.join(dir, 'xml.pt'), 'w') as xml:
      ...   _ = xml.write('''<?xml version="1.0" encoding="utf-8"?>
      ... <rss version="2.0"
      ...     i18n:domain="xml"
      ...     xmlns:i18n="http://xml.zope.org/namespaces/i18n"
      ...     xmlns:tal="http://xml.zope.org/namespaces/tal"
      ...     xmlns="http://purl.org/rss/1.0/modules/content/">
      ...  <channel>
      ...    <link i18n:translate="">Link Content</link>
      ...  </channel>
      ... </rss>
      ... ''')
      >>> extract.tal_strings(dir, domain='xml')
      {u'Link Content': [('...xml.pt', 8)]}

    We also provide a file with a different file ending:

      >>> with open(os.path.join(dir, 'test.html'), 'w') as testpt:
      ...    _ = testpt.write(
      ...         '<tal:block i18n:domain="html"'
      ...         ' i18n:translate="">html</tal:block>')

      >>> extract.tal_strings(dir, domain='html', include_default_domain=True,
      ...                     filePattern='*.html')
      {u'html': [('...test.html', 1)]}

    Cleanup

      >>> import shutil
      >>> shutil.rmtree(dir)
    """
    # We import zope.tal.talgettext here because we can't rely on the
    # right sys path until app_dir has run
    from zope.tal.htmltalparser import HTMLTALParser
    from zope.tal.talgettext import POEngine
    from zope.tal.talgettext import POTALInterpreter
    from zope.tal.talparser import TALParser
    engine = POEngine()

    class Devnull:
        def write(self, s):
            pass

    for filename in find_files(dir, filePattern, exclude=tuple(exclude)):
        with open(filename, 'rb') as f:
            start = f.read(6)

        if start.startswith(b'<?xml'):
            parserFactory = TALParser
        else:
            parserFactory = HTMLTALParser

        try:
            engine.file = filename
            p = parserFactory()
            p.parseFile(filename)
            program, macros = p.getCode()
            POTALInterpreter(program, macros, engine, stream=Devnull(),
                             metal=False)()
        except Exception:  # pragma: no cover
            print('There was an error processing', filename)
            traceback.print_exc()

    # See whether anything in the domain was found
    if domain not in engine.catalog:
        return {}
    # We do not want column numbers.
    catalog = engine.catalog[domain].copy()
    # When the Domain is 'default', then this means that none was found;
    # Include these strings; yes or no?
    if include_default_domain:
        defaultCatalog = engine.catalog.get('default')
        if defaultCatalog is None:
            engine.catalog['default'] = {}
        catalog.update(engine.catalog['default'])
    for msgid, locations in list(catalog.items()):
        catalog[msgid] = [(loc[0], loc[1][0]) for loc in locations]
    return catalog


USAGE = """Program to extract internationalization markup from Python Code,
Page Templates and ZCML.

This tool will extract all findable message strings from all
internationalizable files in your Zope code. It only extracts message
IDs of the specified domain, except in Python code where it extracts
*all* message strings (because it can't detect which domain they are
created with).

Usage: i18nextract -p PATH -s .../site.zcml [options]
Options:
    -p / --path <path>
        Specifies the directory that is supposed to be searched for
        modules (i.e. 'src').  This argument is mandatory.
    -s / --site_zcml <path>
        Specify the location of the root ZCML file to parse (typically
        'site.zcml').  This argument is mandatory
    -d / --domain <domain>
        Specifies the domain that is supposed to be extracted (defaut: 'zope')
    -e / --exclude-default-domain
        Exclude all messages found as part of the default domain. Messages are
        in this domain, if their domain could not be determined. This usually
        happens in page template snippets.
    -o dir
        Specifies a directory, relative to the package in which to put the
        output translation template.
    -x dir
        Specifies a directory, relative to the package, to exclude.
        May be used more than once.
    --python-only
        Only extract message ids from Python
    -h / --help
        Print this message and exit.
"""


def usage(code, msg=''):
    if not msg:
        msg = USAGE
    print(msg, file=sys.stderr)
    sys.exit(code)


def normalize_path(path):
    """Normalize a possibly relative path or symlink"""
    if path == os.path.abspath(path):
        return path

    # This is for symlinks. Thanks to Fred for this trick.
    cwd = os.getcwd()
    if 'PWD' in os.environ:
        cwd = os.environ['PWD']
    return os.path.normpath(os.path.join(cwd, path))


def strip_base_dir(filename, base_dir):
    """Strip base directory from filename if it starts there.

    >>> strip_base_dir('/path/to/base/relpath/to/file',
    ...                '/path/to/base/')
    'relpath/to/file'

    >>> strip_base_dir('/path/to/somewhere/else/relpath/to/file',
    ...                '/path/to/base/')
    '/path/to/somewhere/else/relpath/to/file'

    """
    if filename.startswith(base_dir):
        filename = filename[len(base_dir):]
    return filename


def main(argv=None):
    if argv is None:  # pragma: no cover
        argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(
            argv,
            'hd:s:i:p:o:x:',
            ['help', 'domain=', 'site_zcml=', 'path=', 'python-only'])
    except getopt.error as msg:  # pragma: no cover
        usage(1, msg)

    domain = 'zope'
    path = None
    include_default_domain = True
    output_dir = None
    exclude_dirs = []
    python_only = False
    site_zcml = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-d', '--domain'):
            domain = arg
        elif opt in ('-s', '--site_zcml'):
            if not os.path.exists(arg):
                usage(1, 'The specified location for site.zcml does not exist')
            site_zcml = normalize_path(arg)
        elif opt in ('-e', '--exclude-default-domain'):
            include_default_domain = False
        elif opt in ('-o', ):
            output_dir = arg
        elif opt in ('-x', ):
            exclude_dirs.append(arg)
        elif opt in ('--python-only',):
            python_only = True
        elif opt in ('-p', '--path'):
            if not os.path.exists(arg):
                usage(1, 'The specified path does not exist.')
            path = normalize_path(arg)

    if path is None:
        usage(1, 'You need to provide the module search path with -p PATH.')
    sys.path.insert(0, path)

    if site_zcml is None:
        usage(1, "You need to provide the location of the root ZCML file \n"
                 "(typically 'site.zcml') with -s .../site.zcml.")

    # When generating the comments, we will not need the base directory info,
    # since it is specific to everyone's installation
    src_start = path.rfind('src')
    base_dir = path[:src_start]

    output_file = domain + '.pot'
    if output_dir:
        output_dir = os.path.join(path, output_dir)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, output_file)

    print("base path: %r\n"
          "search path: %s\n"
          "'site.zcml' location: %s\n"
          "exclude dirs: %r\n"
          "domain: %r\n"
          "include default domain: %r\n"
          "output file: %r\n"
          "Python only: %r"
          % (base_dir, path, site_zcml, exclude_dirs, domain,
             include_default_domain, output_file, python_only))

    maker = POTMaker(output_file, path)
    maker.add(py_strings(path, domain, exclude=exclude_dirs), base_dir)
    if not python_only:
        maker.add(zcml_strings(path, domain, site_zcml), base_dir)
        maker.add(tal_strings(path, domain, include_default_domain,
                              exclude=exclude_dirs), base_dir)
    maker.write()
