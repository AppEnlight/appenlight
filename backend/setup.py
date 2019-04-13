import os
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()
CHANGES = open(os.path.join(here, "CHANGELOG.md")).read()

REQUIREMENTS = open(os.path.join(here, "requirements.txt")).readlines()

compiled = re.compile("([^=><]*).*")


def parse_req(req):
    return compiled.search(req).group(1).strip()


if "APPENLIGHT_DEVELOP" in os.environ:
    requires = [_f for _f in map(parse_req, REQUIREMENTS) if _f]
else:
    requires = REQUIREMENTS


def _get_meta_var(name, data, callback_handler=None):
    import re

    matches = re.compile(r"(?:%s)\s*=\s*(.*)" % name).search(data)
    if matches:
        if not callable(callback_handler):
            callback_handler = lambda v: v

        return callback_handler(eval(matches.groups()[0]))


with open(os.path.join(here, "src", "appenlight", "__init__.py"), "r") as _meta:
    _metadata = _meta.read()

__license__ = _get_meta_var("__license__", _metadata)
__author__ = _get_meta_var("__author__", _metadata)
__url__ = _get_meta_var("__url__", _metadata)

found_packages = find_packages("src")
found_packages.append("appenlight.migrations")
found_packages.append("appenlight.migrations.versions")
setup(
    name="appenlight",
    description="appenlight",
    long_description=README,
    classifiers=[
        "Framework :: Pyramid",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Internet :: Log Analysis",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    version="2.0.0rc1",
    license=__license__,
    author=__author__,
    url="https://github.com/AppEnlight/appenlight",
    keywords="web wsgi bfg pylons pyramid flask django monitoring apm instrumentation appenlight",
    python_requires=">=3.5",
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=found_packages,
    include_package_data=True,
    zip_safe=False,
    test_suite="appenlight",
    install_requires=requires,
    extras_require={
        "dev": [
            "coverage",
            "pytest",
            "pyramid",
            "tox",
            "mock",
            "pytest-mock",
            "webtest",
        ],
        "lint": ["black"],
    },
    entry_points={
        "paste.app_factory": ["main = appenlight:main"],
        "console_scripts": [
            "appenlight-cleanup = appenlight.scripts.cleanup:main",
            "appenlight-initializedb = appenlight.scripts.initialize_db:main",
            "appenlight-migratedb = appenlight.scripts.migratedb:main",
            "appenlight-reindex-elasticsearch = appenlight.scripts.reindex_elasticsearch:main",
            "appenlight-static = appenlight.scripts.static:main",
            "appenlight-make-config = appenlight.scripts.make_config:main",
        ],
    },
)
