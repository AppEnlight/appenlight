{ system ? builtins.currentSystem
}:

let

  pkgs = import <nixpkgs> { inherit system; };

  inherit (pkgs) fetchurl fetchgit;

  buildPythonPackage = pkgs.python27Packages.buildPythonPackage;
  python = pkgs.python27Packages.python;

  Jinja2 = buildPythonPackage rec {
    name = "Jinja2-2.7.3";
    src = fetchurl {
      url = "http://pypi.python.org/packages/source/J/Jinja2/${name}.tar.gz";
      md5 = "b9dffd2f3b43d673802fe857c8445b1a";
    };
    propagatedBuildInputs = [ MarkupSafe ];
  };

  MarkupSafe = buildPythonPackage rec {
    name = "MarkupSafe-0.23";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/M/MarkupSafe/${name}.tar.gz";
      md5 = "f5ab3deee4c37cd6a922fb81e730da6e";
    };
  };

  Pygments = buildPythonPackage rec {
    name = "Pygments-2.0.2";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/P/Pygments/${name}.tar.gz";
      md5 = "238587a1370d62405edabd0794b3ec4a";
    };
  };

  alabaster = buildPythonPackage rec {
    name = "alabaster-0.7.3";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/a/alabaster/${name}.tar.gz";
      md5 = "67428d1383fd833f1282fed5deba0898";
    };
  };

  six = buildPythonPackage rec {
    name = "six-1.9.0";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/six/${name}.tar.gz";
      md5 = "476881ef4012262dfc8adc645ee786c4";
    };
  };

  snowballstemmer = buildPythonPackage rec {
    name = "snowballstemmer-1.2.0";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/snowballstemmer/${name}.tar.gz";
      md5 = "51f2ef829db8129dd0f2354f0b209970";
    };
  };

  pytz = buildPythonPackage rec {
    name = "pytz-2015.2";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pytz/${name}.tar.gz";
      md5 = "08440d994cfbbf13d3343362cc3173f7";
    };
  };

  babel = buildPythonPackage rec {
    name = "Babel-1.3";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/B/Babel/${name}.tar.gz";
      md5 = "5264ceb02717843cbc9ffce8e6e06bdb";
    };
    propagatedBuildInputs = [
    pytz
    ];
  };

  Sphinx = buildPythonPackage (rec {
    name = "Sphinx-1.3.1";
    src = fetchurl {
      url = "http://pypi.python.org/packages/source/S/Sphinx/${name}.tar.gz";
      md5 = "8786a194acf9673464c5455b11fd4332";
    };
    propagatedBuildInputs = [
      docutils
      Jinja2
      Pygments
      alabaster
      six
      snowballstemmer
      pytz
      babel

      # TODO: johbo: Had to include it here so that can be imported
      sphinx_rtd_theme
    ];
  });

  docutils = buildPythonPackage rec {
    name = "docutils-0.12";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/d/docutils/${name}.tar.gz";
      md5 = "4622263b62c5c771c03502afa3157768";
    };
  };

  sphinx_rtd_theme = buildPythonPackage rec {
    name = "sphinx_rtd_theme-0.1.9";
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/sphinx_rtd_theme/${name}.tar.gz";
      md5 = "86a25c8d47147c872e42dc84cc66f97b";
    };

    # johbo: Sphinx needs this package and this package needs sphinx, ignore
    # the requirements file to solve this cycle.
    postPatch = ''
      rm requirements.txt
      touch requirements.txt
    '';

    # TODO: johbo: Tests would require sphinx and this creates recursion issues
    doCheck = false;
  };

in python.buildEnv.override {
  inherit python;
  extraLibs = [
    Sphinx
    sphinx_rtd_theme
  ];
}
