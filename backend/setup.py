import os
import sys
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGELOG.rst')).read()

REQUIREMENTS = open(os.path.join(here, 'requirements.txt')).readlines()

compiled = re.compile('([^=><]*).*')


def parse_req(req):
    return compiled.search(req).group(1).strip()


requires = [_f for _f in map(parse_req, REQUIREMENTS) if _f]


def _get_meta_var(name, data, callback_handler=None):
    import re
    matches = re.compile(r'(?:%s)\s*=\s*(.*)' % name).search(data)
    if matches:
        if not callable(callback_handler):
            callback_handler = lambda v: v

        return callback_handler(eval(matches.groups()[0]))

with open(os.path.join(here, 'src', 'appenlight', '__init__.py'), 'r') as _meta:
    _metadata = _meta.read()

with open(os.path.join('src', 'appenlight', 'VERSION')) as _meta_version:
    __version__ = _meta_version.read().strip()

__license__ = _get_meta_var('__license__', _metadata)
__author__ = _get_meta_var('__author__', _metadata)
__url__ = _get_meta_var('__url__', _metadata)

found_packages = find_packages('src')
found_packages.append('appenlight.migrations.versions')
setup(name='appenlight',
      description='appenlight',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      version=__version__,
      license=__license__,
      author=__author__,
      url=__url__,
      keywords='web wsgi bfg pylons pyramid',
      package_dir={'': 'src'},
      packages=found_packages,
      include_package_data=True,
      zip_safe=False,
      test_suite='appenlight',
      install_requires=requires,
      entry_points={
          'paste.app_factory': [
              'main = appenlight:main'
          ],
          'console_scripts': [
              'appenlight-cleanup = appenlight.scripts.cleanup:main',
              'appenlight-initializedb = appenlight.scripts.initialize_db:main',
              'appenlight-migratedb = appenlight.scripts.migratedb:main',
              'appenlight-reindex-elasticsearch = appenlight.scripts.reindex_elasticsearch:main',
              'appenlight-static = appenlight.scripts.static:main',
              'appenlight-make-config = appenlight.scripts.make_config:main',
          ]
      }
      )
