{
  Jinja2 = super.buildPythonPackage {
    name = "Jinja2-2.8";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [MarkupSafe];
    src = fetchurl {
      url = "https://pypi.python.org/packages/f2/2f/0b98b06a345a761bec91a079ccae392d282690c2d8272e708f4d10829e22/Jinja2-2.8.tar.gz";
      md5 = "edb51693fe22c53cee5403775c71a99e";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  Mako = super.buildPythonPackage {
    name = "Mako-1.0.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [MarkupSafe];
    src = fetchurl {
      url = "https://pypi.python.org/packages/7a/ae/925434246ee90b42e8ef57d3b30a0ab7caf9a2de3e449b876c56dcb48155/Mako-1.0.4.tar.gz";
      md5 = "c5fc31a323dd4990683d2f2da02d4e20";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  MarkupSafe = super.buildPythonPackage {
    name = "MarkupSafe-0.23";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/c0/41/bae1254e0396c0cc8cf1751cb7d9afc90a602353695af5952530482c963f/MarkupSafe-0.23.tar.gz";
      md5 = "f5ab3deee4c37cd6a922fb81e730da6e";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  PasteDeploy = super.buildPythonPackage {
    name = "PasteDeploy-1.5.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/0f/90/8e20cdae206c543ea10793cbf4136eb9a8b3f417e04e40a29d72d9922cbd/PasteDeploy-1.5.2.tar.gz";
      md5 = "352b7205c78c8de4987578d19431af3b";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  SQLAlchemy = super.buildPythonPackage {
    name = "SQLAlchemy-1.0.12";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/5c/52/9b48cd58eac58cae2a27923ff34c783f390b95413ff65669a86e98f80829/SQLAlchemy-1.0.12.tar.gz";
      md5 = "6d19ef29883bbebdcac6613cf391cac4";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  WebOb = super.buildPythonPackage {
    name = "WebOb-1.6.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/5d/c7/7c1565b188d8d32bf3657a24b9d71621e35ba20ec4179a0a7f9803511099/WebOb-1.6.1.tar.gz";
      md5 = "04049d82e9d12dd91f6f46f54cc826aa";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  alembic = super.buildPythonPackage {
    name = "alembic-0.8.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [SQLAlchemy Mako python-editor];
    src = fetchurl {
      url = "https://pypi.python.org/packages/d2/c3/fdb752aa39832d056aeac958f35f1fb9fb9397a52bdab9248adcbd9f17d9/alembic-0.8.6.tar.gz";
      md5 = "6517b160e576cedf9b7625a18a9bc594";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  amqp = super.buildPythonPackage {
    name = "amqp-1.4.9";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/cc/a4/f265c6f9a7eb1dd45d36d9ab775520e07ff575b11ad21156f9866da047b2/amqp-1.4.9.tar.gz";
      md5 = "df57dde763ba2dea25b3fa92dfe43c19";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal { fullName = "LGPL"; } { fullName = "GNU Library or Lesser General Public License (LGPL)"; } ];
    };
  };
  anyjson = super.buildPythonPackage {
    name = "anyjson-0.3.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/c3/4d/d4089e1a3dd25b46bebdb55a992b0797cff657b4477bc32ce28038fdecbc/anyjson-0.3.3.tar.gz";
      md5 = "2ea28d6ec311aeeebaf993cb3008b27c";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  appenlight = super.buildPythonPackage {
    name = "appenlight-0.9.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [repoze.sendmail pyramid pyramid-tm pyramid-debugtoolbar pyramid-authstack SQLAlchemy alembic webhelpers2 transaction zope.sqlalchemy pyramid-mailer redis redlock-py pyramid-jinja2 psycopg2 wtforms celery formencode psutil ziggurat-foundations bcrypt appenlight-client markdown colander defusedxml dogpile.cache pyramid-redis-sessions simplejson waitress gunicorn requests requests-oauthlib gevent gevent-websocket pygments lxml paginate paginate-sqlalchemy pyelasticsearch six mock itsdangerous camplight jira python-dateutil authomatic cryptography webassets];
    src = ./.;
    meta = {
      license = [ { fullName = "AGPLv3, and Commercial License"; } ];
    };
  };
  appenlight-client = super.buildPythonPackage {
    name = "appenlight-client-0.6.17";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [WebOb requests six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/af/86/1075f162d6534080f7f6ed9d8a83254e8f0be90c0a3e7ead9feffbe4423f/appenlight_client-0.6.17.tar.gz";
      md5 = "2f4d8229ce2dba607a9077210857e0e5";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal { fullName = "DFSG approved"; } ];
    };
  };
  authomatic = super.buildPythonPackage {
    name = "authomatic-0.1.0.post1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/08/1a/8a930461e604c2d5a7a871e1ac59fa82ccf994c32e807230c8d2fb07815a/Authomatic-0.1.0.post1.tar.gz";
      md5 = "be3f3ce08747d776aae6d6cc8dcb49a9";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  bcrypt = super.buildPythonPackage {
    name = "bcrypt-2.0.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [cffi six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/11/7d/4c7980d04314466de42ea804db71995c9b3a2a47dc79a63c51f1be0cfd50/bcrypt-2.0.0.tar.gz";
      md5 = "e7fb17be46904cdb2ae6a062859ee58c";
    };
    meta = {
      license = [ pkgs.lib.licenses.asl20 ];
    };
  };
  billiard = super.buildPythonPackage {
    name = "billiard-3.3.0.23";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/64/a6/d7b6fb7bd0a4680a41f1d4b27061c7b768c673070ba8ac116f865de4e7ca/billiard-3.3.0.23.tar.gz";
      md5 = "6ee416e1e7c8d8164ce29d7377cca6a4";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  camplight = super.buildPythonPackage {
    name = "camplight-0.9.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [requests];
    src = fetchurl {
      url = "https://pypi.python.org/packages/60/df/bed89a1f1d06632b192eff09a8fa75f85e0080ff70229c8145fbc3b2afa8/camplight-0.9.6.tar.gz";
      md5 = "716cc7a4ea30da34ae4fcbfe2784ce59";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  celery = super.buildPythonPackage {
    name = "celery-3.1.23";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pytz billiard kombu];
    src = fetchurl {
      url = "https://pypi.python.org/packages/ea/a6/6da0bac3ea8abbc2763fd2664af2955702f97f140f2d7277069445532b7c/celery-3.1.23.tar.gz";
      md5 = "c6f10f956a49424d553ab1391ab39ab2";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  certifi = super.buildPythonPackage {
    name = "certifi-2016.8.31";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/1c/d1/0133a5084f0d17db0270c6061e824a11b0e417d743f5ff4c594f4090ed89/certifi-2016.8.31.tar.gz";
      md5 = "2f22d484a36d38d98be74f9eeb2846ec";
    };
    meta = {
      license = [ pkgs.lib.licenses.isc ];
    };
  };
  cffi = super.buildPythonPackage {
    name = "cffi-1.8.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pycparser];
    src = fetchurl {
      url = "https://pypi.python.org/packages/b8/21/9d6f08d2d36a0a8c84623646b4ed5a07023d868823361a086b021fb21172/cffi-1.8.2.tar.gz";
      md5 = "538f307b6c5169bba41fbfda2b070762";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  colander = super.buildPythonPackage {
    name = "colander-1.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [translationstring iso8601];
    src = fetchurl {
      url = "https://pypi.python.org/packages/14/23/c9ceba07a6a1dc0eefbb215fc0dc64aabc2b22ee756bc0f0c13278fa0887/colander-1.2.tar.gz";
      md5 = "83db21b07936a0726e588dae1914b9ed";
    };
    meta = {
      license = [ { fullName = "BSD-derived (http://www.repoze.org/LICENSE.txt)"; } ];
    };
  };
  cryptography = super.buildPythonPackage {
    name = "cryptography-1.2.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [idna pyasn1 six setuptools enum34 ipaddress cffi];
    src = fetchurl {
      url = "https://pypi.python.org/packages/8b/7d/9df253f059c8d9a9389f06df5d6301b0725a44dbf055a1f7aff8e455746a/cryptography-1.2.3.tar.gz";
      md5 = "5474d2b3e8c7555a60852e48d2743f85";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal { fullName = "BSD or Apache License, Version 2.0"; } pkgs.lib.licenses.asl20 ];
    };
  };
  defusedxml = super.buildPythonPackage {
    name = "defusedxml-0.4.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/09/3b/b1afa9649f48517d027e99413fec54f387f648c90156b3cf6451c8cd45f9/defusedxml-0.4.1.tar.gz";
      md5 = "230a5eff64f878b392478e30376d673a";
    };
    meta = {
      license = [ pkgs.lib.licenses.psfl ];
    };
  };
  dogpile.cache = super.buildPythonPackage {
    name = "dogpile.cache-0.5.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [dogpile.core];
    src = fetchurl {
      url = "https://pypi.python.org/packages/07/74/2a83bedf758156d9c95d112691bbad870d3b77ccbcfb781b4ef836ea7d96/dogpile.cache-0.5.7.tar.gz";
      md5 = "3e58ce41af574aab41d78e9c4190f194";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  dogpile.core = super.buildPythonPackage {
    name = "dogpile.core-0.4.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/0e/77/e72abc04c22aedf874301861e5c1e761231c288b5de369c18be8f4b5c9bb/dogpile.core-0.4.1.tar.gz";
      md5 = "01cb19f52bba3e95c9b560f39341f045";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  elasticsearch = super.buildPythonPackage {
    name = "elasticsearch-1.9.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [urllib3];
    src = fetchurl {
      url = "https://pypi.python.org/packages/13/9b/540e311b31a10c2a904acfb08030c656047e5c7ba479d35df2799e5dccfe/elasticsearch-1.9.0.tar.gz";
      md5 = "3550390baea1639479f79758d66ab032";
    };
    meta = {
      license = [ pkgs.lib.licenses.asl20 ];
    };
  };
  enum34 = super.buildPythonPackage {
    name = "enum34-1.1.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/bf/3e/31d502c25302814a7c2f1d3959d2a3b3f78e509002ba91aea64993936876/enum34-1.1.6.tar.gz";
      md5 = "5f13a0841a61f7fc295c514490d120d0";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  formencode = super.buildPythonPackage {
    name = "formencode-1.3.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/99/5b/f71f36b81b42291a70f61104d0eeb1a30be856a052ebe032c37b45db840c/FormEncode-1.3.0.zip";
      md5 = "6df12d60bf3179402f2c2efd1129eb74";
    };
    meta = {
      license = [ pkgs.lib.licenses.psfl ];
    };
  };
  gevent = super.buildPythonPackage {
    name = "gevent-1.1.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [greenlet];
    src = fetchurl {
      url = "https://pypi.python.org/packages/12/dc/0b2e57823225de86f6e111a65d212c9e3b64847dddaa19691a6cb94b0b2e/gevent-1.1.1.tar.gz";
      md5 = "1532f5396ab4d07a231f1935483be7c3";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  gevent-websocket = super.buildPythonPackage {
    name = "gevent-websocket-0.9.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [gevent];
    src = fetchurl {
      url = "https://pypi.python.org/packages/de/93/6bc86ddd65435a56a2f2ea7cc908d92fea894fc08e364156656e71cc1435/gevent-websocket-0.9.5.tar.gz";
      md5 = "03a8473b9a61426b0ef6094319141389";
    };
    meta = {
      license = [ { fullName = "Copyright 2011-2013 Jeffrey Gelens <jeffrey@noppo.pro>"; } pkgs.lib.licenses.asl20 ];
    };
  };
  greenlet = super.buildPythonPackage {
    name = "greenlet-0.4.10";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/67/62/ca2a95648666eaa2ffeb6a9b3964f21d419ae27f82f2e66b53da5b943fc4/greenlet-0.4.10.zip";
      md5 = "bed0c4b3b896702131f4d5c72f87c41d";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  gunicorn = super.buildPythonPackage {
    name = "gunicorn-19.4.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/1e/67/95248e17050822ab436c8a43dbfc0625a8545775737e33b66508cffad278/gunicorn-19.4.5.tar.gz";
      md5 = "ce45c2dccba58784694dd77f23d9a677";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  idna = super.buildPythonPackage {
    name = "idna-2.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/fb/84/8c27516fbaa8147acd2e431086b473c453c428e24e8fb99a1d89ce381851/idna-2.1.tar.gz";
      md5 = "f6473caa9c5e0cc1ad3fd5d04c3c114b";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal { fullName = "BSD-like"; } ];
    };
  };
  ipaddress = super.buildPythonPackage {
    name = "ipaddress-1.0.17";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/bb/26/3b64955ff73f9e3155079b9ed31812afdfa5333b5c76387454d651ef593a/ipaddress-1.0.17.tar.gz";
      md5 = "8bbf0326719fafb1f453921ef96729fe";
    };
    meta = {
      license = [ pkgs.lib.licenses.psfl ];
    };
  };
  iso8601 = super.buildPythonPackage {
    name = "iso8601-0.1.11";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/c0/75/c9209ee4d1b5975eb8c2cba4428bde6b61bd55664a98290dd015cdb18e98/iso8601-0.1.11.tar.gz";
      md5 = "b06d11cd14a64096f907086044f0fe38";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  itsdangerous = super.buildPythonPackage {
    name = "itsdangerous-0.24";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/dc/b4/a60bcdba945c00f6d608d8975131ab3f25b22f2bcfe1dab221165194b2d4/itsdangerous-0.24.tar.gz";
      md5 = "a3d55aa79369aef5345c036a8a26307f";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  jira = super.buildPythonPackage {
    name = "jira-1.0.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [requests requests-oauthlib tlslite six requests-toolbelt];
    src = fetchurl {
      url = "https://pypi.python.org/packages/4e/36/4f0ab121c3510fce29743c31e2f47e99c2be68ee4441ad395366489351b0/jira-1.0.7.tar.gz";
      md5 = "cb1d3f1e1b7a388932ad5d961bf2c56d";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  kombu = super.buildPythonPackage {
    name = "kombu-3.0.35";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [anyjson amqp];
    src = fetchurl {
      url = "https://pypi.python.org/packages/5f/4f/3859b52f6d465d0d4a767516c924ee4f0e1387498ac8d0c30d9942da3762/kombu-3.0.35.tar.gz";
      md5 = "6483ac8ba7109ec606f5cb9bd084b6ef";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  lxml = super.buildPythonPackage {
    name = "lxml-3.6.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/11/1b/fe6904151b37a0d6da6e60c13583945f8ce3eae8ebd0ec763ce546358947/lxml-3.6.0.tar.gz";
      md5 = "5957cc384bd6e83934be35c057ec03b6";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  markdown = super.buildPythonPackage {
    name = "markdown-2.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/16/7f/034572fbc66f76a626156c9500349f5b384ca1f38194318ddde32bc2fcb0/Markdown-2.5.zip";
      md5 = "053e5614f7efc06ac0fcd6954678096c";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  mock = super.buildPythonPackage {
    name = "mock-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/15/45/30273ee91feb60dabb8fbb2da7868520525f02cf910279b3047182feed80/mock-1.0.1.zip";
      md5 = "869f08d003c289a97c1a6610faf5e913";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  oauthlib = super.buildPythonPackage {
    name = "oauthlib-2.0.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/ce/92/7f07412a4f04e55c1e83a09c6fd48075b5df96c1dbd4078c3407c5be1dff/oauthlib-2.0.0.tar.gz";
      md5 = "79b83aa677fc45d1ea28deab7445b4ca";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal { fullName = "OSI Approved"; } ];
    };
  };
  paginate = super.buildPythonPackage {
    name = "paginate-0.5.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/52/2e/2c3a5647d3f7583355743d73841d03c8b50b97983a478a8f82d3cb9f4a5f/paginate-0.5.4.tar.gz";
      md5 = "91fdb133f85ac73c6616feba38976e95";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  paginate-sqlalchemy = super.buildPythonPackage {
    name = "paginate-sqlalchemy-0.2.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [SQLAlchemy paginate];
    src = fetchurl {
      url = "https://pypi.python.org/packages/25/64/fe572514615971fc235e95798ae0e2ee3beeccf43272c623a0a6b082d2d6/paginate_sqlalchemy-0.2.0.tar.gz";
      md5 = "4ca097c4132f43cd72c6a1795b6bbb5d";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  passlib = super.buildPythonPackage {
    name = "passlib-1.6.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/1e/59/d1a50836b29c87a1bde9442e1846aa11e1548491cbee719e51b45a623e75/passlib-1.6.5.tar.gz";
      md5 = "d2edd6c42cde136a538b48d90a06ad67";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  psutil = super.buildPythonPackage {
    name = "psutil-2.1.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/53/6a/8051b913b2f94eb00fd045fe9e14a7182b6e7f088b12c308edd7616a559b/psutil-2.1.2.tar.gz";
      md5 = "1969c9b3e256f5ce8fb90c5d0124233e";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  psycopg2 = super.buildPythonPackage {
    name = "psycopg2-2.6.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/86/fd/cc8315be63a41fe000cce20482a917e874cdc1151e62cb0141f5e55f711e/psycopg2-2.6.1.tar.gz";
      md5 = "842b44f8c95517ed5b792081a2370da1";
    };
    meta = {
      license = [ pkgs.lib.licenses.zpt21 { fullName = "GNU Library or Lesser General Public License (LGPL)"; } { fullName = "LGPL with exceptions or ZPL"; } ];
    };
  };
  pyasn1 = super.buildPythonPackage {
    name = "pyasn1-0.1.9";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/f7/83/377e3dd2e95f9020dbd0dfd3c47aaa7deebe3c68d3857a4e51917146ae8b/pyasn1-0.1.9.tar.gz";
      md5 = "f00a02a631d4016818659d1cc38d229a";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  pycparser = super.buildPythonPackage {
    name = "pycparser-2.14";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/6d/31/666614af3db0acf377876d48688c5d334b6e493b96d21aa7d332169bee50/pycparser-2.14.tar.gz";
      md5 = "a2bc8d28c923b4fe2b2c3b4b51a4f935";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  pyelasticsearch = super.buildPythonPackage {
    name = "pyelasticsearch-1.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [certifi elasticsearch urllib3 simplejson six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/2f/3a/7643cfcfc4cbdbb20ada800bbd54ac9705d0c047d7b8f8d5eeeb3047b4eb/pyelasticsearch-1.4.tar.gz";
      md5 = "ed61ebb7b253364e55b4923d11e17049";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  pygments = super.buildPythonPackage {
    name = "pygments-2.1.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/b8/67/ab177979be1c81bc99c8d0592ef22d547e70bb4c6815c383286ed5dec504/Pygments-2.1.3.tar.gz";
      md5 = "ed3fba2467c8afcda4d317e4ef2c6150";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  pyramid = super.buildPythonPackage {
    name = "pyramid-1.7.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools WebOb repoze.lru zope.interface zope.deprecation venusian translationstring PasteDeploy];
    src = fetchurl {
      url = "https://pypi.python.org/packages/9c/6d/9b9f9acf22c5d221f25cf6756645bce9ea54ee741466197674fe77f2eee3/pyramid-1.7.3.tar.gz";
      md5 = "5f154c8c352ef013e6e412be02bbb576";
    };
    meta = {
      license = [ { fullName = "Repoze Public License"; } { fullName = "BSD-derived (http://www.repoze.org/LICENSE.txt)"; } ];
    };
  };
  pyramid-authstack = super.buildPythonPackage {
    name = "pyramid-authstack-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyramid zope.interface];
    src = fetchurl {
      url = "https://pypi.python.org/packages/01/4b/e84cb8fda19f0f03f96231195fd074212b9291f732aa07f90edcfb21ff34/pyramid_authstack-1.0.1.tar.gz";
      md5 = "8e199862b5a5cd6385f7d5209cee2f12";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal pkgs.lib.licenses.mit ];
    };
  };
  pyramid-debugtoolbar = super.buildPythonPackage {
    name = "pyramid-debugtoolbar-3.0.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyramid pyramid-mako repoze.lru pygments];
    src = fetchurl {
      url = "https://pypi.python.org/packages/b0/c5/aae5d99983600146875d471aab9142b925fd3596e6e637f6c35d158d09cc/pyramid_debugtoolbar-3.0.4.tar.gz";
      md5 = "51ff68a733ae994641027f10116e519d";
    };
    meta = {
      license = [ { fullName = "Repoze Public License"; } pkgs.lib.licenses.bsdOriginal ];
    };
  };
  pyramid-jinja2 = super.buildPythonPackage {
    name = "pyramid-jinja2-2.6.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyramid zope.deprecation Jinja2 MarkupSafe];
    src = fetchurl {
      url = "https://pypi.python.org/packages/37/00/ac38702305dcf08fe1f1d6d882e8e2d957543bc96c62de52d99d43433c23/pyramid_jinja2-2.6.2.tar.gz";
      md5 = "10ca075934ebf8f52acfc9898991966d";
    };
    meta = {
      license = [ { fullName = "Repoze Public License"; } { fullName = "BSD-derived (http://www.repoze.org/LICENSE.txt)"; } ];
    };
  };
  pyramid-mailer = super.buildPythonPackage {
    name = "pyramid-mailer-0.14.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyramid repoze.sendmail];
    src = fetchurl {
      url = "https://pypi.python.org/packages/43/02/a32823750dbdee4280090843d5788cc550ab6f24f23fcabbeb7f912bf5fe/pyramid_mailer-0.14.1.tar.gz";
      md5 = "a589801afdc4a3d64337e4cbd2fc7cdb";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  pyramid-mako = super.buildPythonPackage {
    name = "pyramid-mako-1.0.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyramid Mako];
    src = fetchurl {
      url = "https://pypi.python.org/packages/f1/92/7e69bcf09676d286a71cb3bbb887b16595b96f9ba7adbdc239ffdd4b1eb9/pyramid_mako-1.0.2.tar.gz";
      md5 = "ee25343a97eb76bd90abdc2a774eb48a";
    };
    meta = {
      license = [ { fullName = "Repoze Public License"; } { fullName = "BSD-derived (http://www.repoze.org/LICENSE.txt)"; } ];
    };
  };
  pyramid-redis-sessions = super.buildPythonPackage {
    name = "pyramid-redis-sessions-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [redis pyramid];
    src = fetchurl {
      url = "https://pypi.python.org/packages/45/9b/905fd70bb603b61819d525efe7626342ad5f8d033e25fbaedbc53f458c37/pyramid_redis_sessions-1.0.1.tar.gz";
      md5 = "a39bbfd36f61685eac32d5f4010d3fef";
    };
    meta = {
      license = [ { fullName = "FreeBSD"; } ];
    };
  };
  pyramid-tm = super.buildPythonPackage {
    name = "pyramid-tm-0.12";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyramid transaction];
    src = fetchurl {
      url = "https://pypi.python.org/packages/3e/0b/a0fd3856c8ca2b30f20fcd26627b9cf9d91cd2cfabae42aee3441b2441c5/pyramid_tm-0.12.tar.gz";
      md5 = "6e5f4449706855fdb7c63d2190e0209b";
    };
    meta = {
      license = [ { fullName = "Repoze Public License"; } { fullName = "BSD-derived (http://www.repoze.org/LICENSE.txt)"; } ];
    };
  };
  python-dateutil = super.buildPythonPackage {
    name = "python-dateutil-2.5.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/3e/f5/aad82824b369332a676a90a8c0d1e608b17e740bbb6aeeebca726f17b902/python-dateutil-2.5.3.tar.gz";
      md5 = "05ffc6d2cc85a7fd93bb245807f715ef";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal { fullName = "Simplified BSD"; } ];
    };
  };
  python-editor = super.buildPythonPackage {
    name = "python-editor-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/2b/c0/df7b87d5cf016f82eab3b05cd35f53287c1178ad8c42bfb6fa61b89b22f6/python-editor-1.0.1.tar.gz";
      md5 = "e1fa63535b40e022fa4fd646fd8b511a";
    };
    meta = {
      license = [ pkgs.lib.licenses.asl20 { fullName = "Apache"; } ];
    };
  };
  pytz = super.buildPythonPackage {
    name = "pytz-2016.6.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/5d/8e/6635d8f3f9f48c03bb925fab543383089858271f9cfd1216b83247e8df94/pytz-2016.6.1.tar.gz";
      md5 = "b6c28a3b968bc1d8badfb61b93874e03";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  redis = super.buildPythonPackage {
    name = "redis-2.10.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/68/44/5efe9e98ad83ef5b742ce62a15bea609ed5a0d1caf35b79257ddb324031a/redis-2.10.5.tar.gz";
      md5 = "3b26c2b9703b4b56b30a1ad508e31083";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  redlock-py = super.buildPythonPackage {
    name = "redlock-py-1.0.8";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [redis];
    src = fetchurl {
      url = "https://pypi.python.org/packages/7c/40/29e1730f771b5d27e3c77b5426b6a67a3642868bf8bd592dfa6639feda98/redlock-py-1.0.8.tar.gz";
      md5 = "7f8fe8ddefbe35deaa64d67ebdf1c58e";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  repoze.lru = super.buildPythonPackage {
    name = "repoze.lru-0.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/6e/1e/aa15cc90217e086dc8769872c8778b409812ff036bf021b15795638939e4/repoze.lru-0.6.tar.gz";
      md5 = "2c3b64b17a8e18b405f55d46173e14dd";
    };
    meta = {
      license = [ { fullName = "Repoze Public License"; } { fullName = "BSD-derived (http://www.repoze.org/LICENSE.txt)"; } ];
    };
  };
  repoze.sendmail = super.buildPythonPackage {
    name = "repoze.sendmail-4.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools zope.interface transaction];
    src = fetchurl {
      url = "https://pypi.python.org/packages/6b/3a/501a897c036c7b728b02a2695998055755e9e71c7e135abdcf200958965e/repoze.sendmail-4.1.tar.gz";
      md5 = "81d15f1f03cc67d6f56f2091c594ef57";
    };
    meta = {
      license = [ pkgs.lib.licenses.zpt21 ];
    };
  };
  requests = super.buildPythonPackage {
    name = "requests-2.9.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/f9/6d/07c44fb1ebe04d069459a189e7dab9e4abfe9432adcd4477367c25332748/requests-2.9.1.tar.gz";
      md5 = "0b7f480d19012ec52bab78292efd976d";
    };
    meta = {
      license = [ pkgs.lib.licenses.asl20 ];
    };
  };
  requests-oauthlib = super.buildPythonPackage {
    name = "requests-oauthlib-0.6.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [oauthlib requests];
    src = fetchurl {
      url = "https://pypi.python.org/packages/f9/98/a1aaae4bbcde0e98d6d853c4f08bd52f20b0005cefb881679bcdf7ea7a00/requests-oauthlib-0.6.1.tar.gz";
      md5 = "f159bc7675ebe6a2d76798f4c00c5bf8";
    };
    meta = {
      license = [ pkgs.lib.licenses.isc pkgs.lib.licenses.bsdOriginal ];
    };
  };
  requests-toolbelt = super.buildPythonPackage {
    name = "requests-toolbelt-0.7.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [requests];
    src = fetchurl {
      url = "https://pypi.python.org/packages/59/78/1d391d30ebf74079a8e4de6ab66fdca5362903ef2df64496f4697e9bb626/requests-toolbelt-0.7.0.tar.gz";
      md5 = "bfe2009905f460f4764c32cfbbf4205f";
    };
    meta = {
      license = [ pkgs.lib.licenses.asl20 ];
    };
  };
  setuptools = super.buildPythonPackage {
    name = "setuptools-27.2.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/87/ba/54197971d107bc06f5f3fbdc0d728a7ae0b10cafca46acfddba65a0899d8/setuptools-27.2.0.tar.gz";
      md5 = "b39715612fdc0372dbfd7b3fcf5d4fe5";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  simplejson = super.buildPythonPackage {
    name = "simplejson-3.8.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/f0/07/26b519e6ebb03c2a74989f7571e6ae6b82e9d7d81b8de6fcdbfc643c7b58/simplejson-3.8.2.tar.gz";
      md5 = "53b1371bbf883b129a12d594a97e9a18";
    };
    meta = {
      license = [ { fullName = "Academic Free License (AFL)"; } pkgs.lib.licenses.mit ];
    };
  };
  six = super.buildPythonPackage {
    name = "six-1.9.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/16/64/1dc5e5976b17466fd7d712e59cbe9fb1e18bec153109e5ba3ed6c9102f1a/six-1.9.0.tar.gz";
      md5 = "476881ef4012262dfc8adc645ee786c4";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  tlslite = super.buildPythonPackage {
    name = "tlslite-0.4.9";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/92/2b/7904cf913d9bf150b3e408a92c9cb5ce0b97a9ec19f998af48bf4c607f0e/tlslite-0.4.9.tar.gz";
      md5 = "9f3b3797f595dd66cd36a65c83a87869";
    };
    meta = {
      license = [ { fullName = "public domain and BSD"; } ];
    };
  };
  transaction = super.buildPythonPackage {
    name = "transaction-1.4.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [zope.interface];
    src = fetchurl {
      url = "https://pypi.python.org/packages/9d/9d/afb5c4904fb41edc14029744ff030ac0596846262bda6145edf23791c880/transaction-1.4.3.tar.gz";
      md5 = "b4ca5983c9e3a0808ff5ff7648092c76";
    };
    meta = {
      license = [ pkgs.lib.licenses.zpt21 ];
    };
  };
  translationstring = super.buildPythonPackage {
    name = "translationstring-1.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/5e/eb/bee578cc150b44c653b63f5ebe258b5d0d812ddac12497e5f80fcad5d0b4/translationstring-1.3.tar.gz";
      md5 = "a4b62e0f3c189c783a1685b3027f7c90";
    };
    meta = {
      license = [ { fullName = "BSD-like (http://repoze.org/license.html)"; } ];
    };
  };
  urllib3 = super.buildPythonPackage {
    name = "urllib3-1.17";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/c2/79/8851583070bac203561d21b9478340535893f587759608156aaca60a615a/urllib3-1.17.tar.gz";
      md5 = "12d5520f0fffed0e65cb66b5bdc6ddec";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  venusian = super.buildPythonPackage {
    name = "venusian-1.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/86/20/1948e0dfc4930ddde3da8c33612f6a5717c0b4bc28f591a5c5cf014dd390/venusian-1.0.tar.gz";
      md5 = "dccf2eafb7113759d60c86faf5538756";
    };
    meta = {
      license = [ { fullName = "BSD-derived (http://www.repoze.org/LICENSE.txt)"; } ];
    };
  };
  waitress = super.buildPythonPackage {
    name = "waitress-1.0.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/a5/c3/264a56b2470de29f35dda8369886663303c8a2294673b2e6b9975e59f471/waitress-1.0.0.tar.gz";
      md5 = "b900c4d793e218d77742f47ece58dd43";
    };
    meta = {
      license = [ pkgs.lib.licenses.zpt21 ];
    };
  };
  webassets = super.buildPythonPackage {
    name = "webassets-0.11.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/0e/97/f0cd013a3ae074672e9fdfa8629e4071b5cc420a2c82bef5622a87631d1c/webassets-0.11.1.tar.gz";
      md5 = "6acca51bd12fbdc0399ab1a9b67a1599";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  webhelpers2 = super.buildPythonPackage {
    name = "webhelpers2-2.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [MarkupSafe six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/ff/30/56342c6ea522439e3662427c8d7b5e5b390dff4ff2dc92d8afcb8ab68b75/WebHelpers2-2.0.tar.gz";
      md5 = "0f6b68d70c12ee0aed48c00b24da13d3";
    };
    meta = {
      license = [ pkgs.lib.licenses.mit ];
    };
  };
  wtforms = super.buildPythonPackage {
    name = "wtforms-2.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/bf/91/2e553b86c55e9cf2f33265de50e052441fb753af46f5f20477fe9c61280e/WTForms-2.1.zip";
      md5 = "6938a541fafd1a1ae2f6b9b88588eef2";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  ziggurat-foundations = super.buildPythonPackage {
    name = "ziggurat-foundations-0.6.8";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [SQLAlchemy passlib paginate paginate-sqlalchemy alembic six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/b2/3c/f9a0112a30424a58fccdd357338b4559fdda9e1bb3c9611b1ad263abf49e/ziggurat_foundations-0.6.8.tar.gz";
      md5 = "d2cc7201667b0e01099456a77726179c";
    };
    meta = {
      license = [ pkgs.lib.licenses.bsdOriginal ];
    };
  };
  zope.deprecation = super.buildPythonPackage {
    name = "zope.deprecation-4.1.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools];
    src = fetchurl {
      url = "https://pypi.python.org/packages/c1/d3/3919492d5e57d8dd01b36f30b34fc8404a30577392b1eb817c303499ad20/zope.deprecation-4.1.2.tar.gz";
      md5 = "e9a663ded58f4f9f7881beb56cae2782";
    };
    meta = {
      license = [ pkgs.lib.licenses.zpt21 ];
    };
  };
  zope.interface = super.buildPythonPackage {
    name = "zope.interface-4.3.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools];
    src = fetchurl {
      url = "https://pypi.python.org/packages/38/1b/d55c39f2cf442bd9fb2c59760ed058c84b57d25c680819c25f3aff741e1f/zope.interface-4.3.2.tar.gz";
      md5 = "5f7e15a5bcdfa3c6c0e93ffe45caf87c";
    };
    meta = {
      license = [ pkgs.lib.licenses.zpt21 ];
    };
  };
  zope.sqlalchemy = super.buildPythonPackage {
    name = "zope.sqlalchemy-0.7.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools SQLAlchemy transaction zope.interface];
    src = fetchurl {
      url = "https://pypi.python.org/packages/d0/e0/5df0d7f9f1955e2e2edecbb1367cf1fa76bc2f84d700661ffd4161c7e2e9/zope.sqlalchemy-0.7.6.zip";
      md5 = "0f5bf14679951e59007e090b6922688c";
    };
    meta = {
      license = [ pkgs.lib.licenses.zpt21 ];
    };
  };

### Test requirements

  
}
