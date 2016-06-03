import os
import sys
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

REQUIREMENTS = open(os.path.join(here, 'requirements.txt')).readlines()

compiled = re.compile('([^=><]*).*')


def parse_req(req):
    return compiled.search(req).group(1).strip()


requires = [_f for _f in map(parse_req, REQUIREMENTS) if _f]

if sys.version_info[:3] < (2, 5, 0):
    requires.append('pysqlite')

found_packages = find_packages('src')
found_packages.append('appenlight.migrations.versions')
setup(name='appenlight',
      version='0.1',
      description='appenlight',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
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
