import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.ALDocument',
      version='0.0.10',
      description=('A docassemble extension.'),
      long_description='# docassemble.ALDocument\r\n\r\nA package to help manage docassemble interviews that assemble multiple documents.\r\n\r\nALDocument is a single object that represents a document with a "preview"\r\nversion (perhaps without a signature) and a "final" version, as well as an\r\naddendum, which is often needed for PDF forms.\r\n\r\nThe ALAddendumFieldDict object is an ordered dict that stores a collection of field names, together with a\r\ncharacter/item limit. The ALDocument uses this list to automatically include\r\nan addendum when it is needed. One addendum template can easily be shared\r\nacross multiple documents that your interview assembles.\r\n\r\nALDocumentBundle is an object that can represent a list of ALDocuments in\r\na structured order. One interview may mix and match the same templates into\r\nmultiple "bundles". E.g., one set of cover instructions might be sent to the \r\nuser and one to the court. Bundles also handle ALDocuments that are "enabled" or\r\n"disabled". You may allow the user to control which documents are assembled \r\nmanually, or the interview logic might control which documents ultimately are\r\nassembled. The ALDocumentBundle will handle assembling just the "enabled"\r\ndocuments. Bundles can be nested for convenience.\r\n\r\nALDocumentBundle.download_buttons_html() generates a table with download/view\r\nbuttons for the generated document, a slightly neater format than the \r\ndocassemble default when there is a larger list of documents.\r\n',
      long_description_content_type='text/markdown',
      author='System Administrator',
      author_email='admin@admin.com',
      license='The MIT License (MIT)',
      url='https://docassemble.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=[],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/ALDocument/', package='docassemble.ALDocument'),
     )

