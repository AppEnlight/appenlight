{ system ? builtins.currentSystem
}:
let
pkgs = import <nixpkgs> { inherit system; };
inherit (pkgs) fetchurl fetchgit;
buildPythonPackage = pkgs.python27Packages.buildPythonPackage;
python = pkgs.python27Packages.python;



AnyKeystore = buildPythonPackage rec {
  name = "anykeystore-0.2";
  propagatedBuildInputs = [
      pkgs.python27Packages.unittest2
      pkgs.python27Packages.mock
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/a/anykeystore/${name}.tar.gz";
  md5 = "cc331cc5aa6eea38e498cd9cd73e8241";
  };
};


Ordereddict = buildPythonPackage rec {
  name = "ordereddict-1.1";
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/o/ordereddict/${name}.tar.gz";
  md5 = "a0ed854ee442051b249bfad0f638bbec";
  };
};


HTTPPretty = buildPythonPackage rec {
  name = "httpretty-0.8.10";
  propagatedBuildInputs = [
      pkgs.python27Packages.sure
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/h/httpretty/${name}.tar.gz";
  md5 = "9c130b16726cbf85159574ae5761bce7";
  };
  doCheck = false; # error: Could not find suitable distribution for Requirement.parse('sure==1.2.3')
};


Redis = buildPythonPackage rec {
  name = "redis-2.10.3";
  propagatedBuildInputs = [
      pkgs.python27Packages.pytest
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/r/redis/${name}.tar.gz";
  md5 = "7619221ad0cbd124a5687458ea3f5289";
  };
};


PyTestInstaFail = buildPythonPackage rec {
  name = "pytest-instafail-0.3.0";
  propagatedBuildInputs = [
      pkgs.python27Packages.pytest
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/p/pytest-instafail/${name}.tar.gz";
  md5 = "561e8c70038ae07404bdd94b0e0318d6";
  };
};


PythonOpenId = buildPythonPackage rec {
  name = "python-openid-2.2.5";
  propagatedBuildInputs = [
      pkgs.python27Packages.pytest
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/p/python-openid/${name}.tar.gz";
  md5 = "393f48b162ec29c3de9e2973548ea50d";
  };
};


################# DEPS OF DEPS END #######################

AppEnlightClient = buildPythonPackage rec {
  name = "appenlight_client-0.6.14";
  propagatedBuildInputs = [
      pkgs.python27Packages.requests2
      pkgs.python27Packages.webob
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/a/appenlight-client/${name}.tar.gz";
  md5 = "578c69b09f4356d898fff1199b98a95c";
  };
};


PyCountry = buildPythonPackage rec {
  name = "pycountry-1.14";
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/p/pycountry/${name}.tar.gz";
  md5 = "f601972df38b39f02247e218e81ecf71";
  };
};


Camplight = buildPythonPackage rec {
  name = "camplight-0.9.6";
  buildInputs = [
  pkgs.python27Packages.pytest
  pkgs.python27Packages.requests
  pkgs.python27Packages.sure
  HTTPPretty
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/c/camplight/${name}.tar.gz";
  md5 = "716cc7a4ea30da34ae4fcbfe2784ce59";
  };
};


DefusedXML = buildPythonPackage rec {
  name = "defusedxml-0.4.1";
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/d/defusedxml/${name}.tar.gz";
  md5 = "230a5eff64f878b392478e30376d673a";
  };
};


FormEncode = buildPythonPackage rec {
  name = "FormEncode-1.3.0";
  propagatedBuildInputs = [
      pkgs.python27Packages.dns
      pkgs.python27Packages.nose
      PyCountry
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/F/FormEncode/${name}.zip";
  md5 = "6df12d60bf3179402f2c2efd1129eb74";
  };
};


JIRA = buildPythonPackage rec {
  name = "jira-0.50";
  propagatedBuildInputs = [
        pkgs.python27Packages.autopep8
        pkgs.python27Packages.covCore
        pkgs.python27Packages.pytest
        pkgs.python27Packages.pytest_xdist
        pkgs.python27Packages.pytestpep8
        pkgs.python27Packages.pytestcov
        PyTestInstaFail
        pkgs.python27Packages.simplejson
        pkgs.python27Packages.requests2
        pkgs.python27Packages.requests_toolbelt
        pkgs.python27Packages.requests_oauthlib
        pkgs.python27Packages.six
        pkgs.python27Packages.sphinx
        pkgs.python27Packages.tlslite
        Ordereddict
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/j/jira/${name}.tar.gz";
  md5 = "23abea2446beb4161ce50bab13654319";
  };
  doCheck = false;
};


PyElasticsearch = buildPythonPackage rec {
  name = "pyelasticsearch-1.4";
  propagatedBuildInputs = [
        pkgs.python27Packages.six
        pkgs.python27Packages.simplejson
        pkgs.python27Packages.urllib3
        pkgs.python27Packages.elasticsearch
        pkgs.python27Packages.certifi
        pkgs.python27Packages.nose
        pkgs.python27Packages.mock
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/p/pyelasticsearch/${name}.tar.gz";
  md5 = "ed61ebb7b253364e55b4923d11e17049";
  };
};


PyramidAuthStack = buildPythonPackage rec {
  name = "pyramid_authstack-1.0.1";
  propagatedBuildInputs = [
        pkgs.python27Packages.pyramid
        pkgs.python27Packages.mock
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/p/pyramid_authstack/${name}.tar.gz";
  md5 = "8e199862b5a5cd6385f7d5209cee2f12";
  };
};


PyramidRedisSessions = buildPythonPackage rec {
  name = "pyramid_redis_sessions-1.0.1";
  propagatedBuildInputs = [
        pkgs.python27Packages.pyramid
        pkgs.python27Packages.pytest
        pkgs.python27Packages.mock
        Redis
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/p/pyramid_redis_sessions/${name}.tar.gz";
  md5 = "a39bbfd36f61685eac32d5f4010d3fef";
  };
};


RedlockPy = buildPythonPackage rec {
  name = "redlock-py-1.0.5";
  propagatedBuildInputs = [
        Redis
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/r/redlock-py/${name}.tar.gz";
  md5 = "be9da24bf9b360d56ff2b66476879c86";
  };
};

Velruse = buildPythonPackage rec {
  name = "velruse-1.1.1";
  propagatedBuildInputs = [
        AnyKeystore
        PythonOpenId
        pkgs.python27Packages.pyramid
        pkgs.python27Packages.unittest2
        pkgs.python27Packages.requests2
        pkgs.python27Packages.requests_oauthlib
        pkgs.python27Packages.webtest
        pkgs.python27Packages.selenium
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/v/velruse/${name}.tar.gz";
  md5 = "40cc41048817e248d9292933be194eeb";
  };
  doCheck = false; # setting up selenium for this might be complicated :P
};


WTForms = buildPythonPackage rec {
  name = "WTForms-2.0.2";
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/W/WTForms/${name}.zip";
  md5 = "613cf723ab40537705bec02733c78d95";
  };
};


Paginate = buildPythonPackage rec {
  name = "paginate-0.5";
  src = fetchurl {
  url = "https://pypi.python.org/packages/source/p/paginate/${name}.tar.gz";
  md5 = "1f95c4440819d776e3b9ce7dc8dc40a4";
  };
};


PaginateSQLAlchemy = buildPythonPackage rec {
  name = "paginate_sqlalchemy-0.2.0";
  propagatedBuildInputs = [
      Paginate
      pkgs.python27Packages.sqlalchemy9
  ];
  buildInputs = [
      pkgs.python27Packages.sqlalchemy9
  ];
  src = fetchurl {
  url = "https://pypi.python.org/packages/any/p/paginate_sqlalchemy/${name}.tar.gz";
  md5 = "4ca097c4132f43cd72c6a1795b6bbb5d";
  };
};


ZigguratFoundations = buildPythonPackage rec {
  name = "ziggurat_foundations-0.6.2";
  propagatedBuildInputs = [pkgs.python27Full];
  buildInputs = [
      pkgs.python27Full
      pkgs.python27Packages.six
      pkgs.python27Packages.alembic
      pkgs.python27Packages.cryptacular
      pkgs.python27Packages.coverage
      PaginateSQLAlchemy
  ];
  src = fetchurl {
  url = "http://pypi.python.org/packages/source/z/ziggurat-foundations/${name}.tar.gz";
  md5 = "424cf8740f87b12e4728269912f9fc0b";
  };
  doCheck = false;
};

AppEnlight = buildPythonPackage rec {
    name = "appenlight";
    propagatedBuildInputs = [
    pkgs.python27Full
    pkgs.python27Packages.alembic
    AppEnlightClient
    Camplight
    pkgs.python27Packages.celery
    pkgs.python27Packages.colander
    pkgs.python27Packages.cryptacular
    DefusedXML
    pkgs.python27Packages.dogpile_cache
    FormEncode
    pkgs.python27Packages.gevent
    pkgs.python27Packages.gevent-websocket
    pkgs.python27Packages.gunicorn
    JIRA
    pkgs.python27Packages.lxml
    pkgs.python27Packages.markdown
    pkgs.python27Packages.mock
    PaginateSQLAlchemy
    pkgs.python27Packages.psutil
    pkgs.python27Packages.psycopg2
    PyElasticsearch
    pkgs.python27Packages.pygments
    pkgs.python27Packages.pyramid
    pkgs.python27Packages.pyramid_debugtoolbar
    PyramidAuthStack
    pkgs.python27Packages.itsdangerous
    pkgs.python27Packages.jinja2
    pkgs.python27Packages.pyramid_jinja2
    pkgs.python27Packages.pyramid_mailer
    PyramidRedisSessions
    pkgs.python27Packages.pyramid_tm
    pkgs.python27Packages.dateutil
    pkgs.python27Packages.redis
    RedlockPy
    pkgs.python27Packages.requests2
    pkgs.python27Packages.requests_oauthlib
    pkgs.python27Packages.simplejson
    pkgs.python27Packages.six
    pkgs.python27Packages.sqlalchemy9
    pkgs.python27Packages.transaction
    Velruse
    WTForms
    pkgs.python27Packages.waitress
    pkgs.python27Packages.webhelpers
    ZigguratFoundations
    pkgs.python27Packages.zope_sqlalchemy
    ];
    src = ./.;
    doCheck= false;
};


in buildPythonPackage {
    name = "appenlight-env";
    buildInputs = [
    AppEnlight
    ];
    src = ./.;
    doCheck=false;
}
