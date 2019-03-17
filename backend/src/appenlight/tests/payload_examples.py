# -*- coding: utf-8 -*-

# Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-

from datetime import datetime

now = datetime.utcnow().date()

REQUEST_METRICS_EXAMPLES = [
    {
        "server": "some.server.hostname",
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
        "metrics": [
            [
                "dir/module:func",
                {
                    "custom": 0.0,
                    "custom_calls": 0,
                    "main": 0.01664,
                    "nosql": 0.00061,
                    "nosql_calls": 23,
                    "remote": 0.0,
                    "remote_calls": 0,
                    "requests": 1,
                    "sql": 0.00105,
                    "sql_calls": 2,
                    "tmpl": 0.0,
                    "tmpl_calls": 0,
                },
            ],
            [
                "SomeView.function",
                {
                    "custom": 0.0,
                    "custom_calls": 0,
                    "main": 0.647261,
                    "nosql": 0.306554,
                    "nosql_calls": 140,
                    "remote": 0.0,
                    "remote_calls": 0,
                    "requests": 28,
                    "sql": 0.0,
                    "sql_calls": 0,
                    "tmpl": 0.0,
                    "tmpl_calls": 0,
                },
            ],
        ],
    }
]

LOG_EXAMPLES = [
    {
        "log_level": "WARNING",
        "message": "OMG ValueError happened",
        "namespace": "some.namespace.indicator",
        "request_id": "SOME_UUID",
        "server": "some server",
        "tags": [["tag_name", "tag_value"], ["tag_name2", 2]],
        "date": now.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    },
    {
        "log_level": "ERROR",
        "message": "OMG ValueError happened2",
        "namespace": "some.namespace.indicator",
        "request_id": "SOME_UUID",
        "server": "some server",
        "date": now.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    },
]

PARSED_REPORT_404 = {
    "report_details": [
        {
            "username": "foo",
            "url": "http://localhost:6543/test/error?aaa=1&bbb=2",
            "ip": "127.0.0.1",
            "start_time": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
            "slow_calls": [],
            "request": {
                "COOKIES": {
                    "country": "US",
                    "sessionId": "***",
                    "test_group_id": "5",
                    "http_referer": "http://localhost:5000/",
                },
                "POST": {},
                "GET": {"aaa": ["1"], "bbb": ["2"]},
                "HTTP_METHOD": "GET",
            },
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1",
            "message": "",
            "end_time": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
            "request_stats": {},
        }
    ],
    "error": "404 Not Found",
    "server": "servername/instancename",
    "priority": 5,
    "client": "appenlight-python",
    "language": "python",
    "http_status": 404,
}

PYTHON_PAYLOAD_0_4 = {
    "client": "your-client-name-python",
    "language": "python",
    "view_name": "views/foo:bar",
    "server": "servername/instancename",
    "priority": 5,
    "error": "OMG ValueError happened test",
    "occurences": 1,
    "http_status": 500,
    "report_details": [
        {
            "username": "USER",
            "url": "HTTP://SOMEURL",
            "ip": "127.0.0.1",
            "start_time": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
            "end_time": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
            "user_agent": "BROWSER_AGENT",
            "message": "arbitrary text that will get attached to your report",
            "request_id": "SOME_UUID",
            "request": {
                "REQUEST_METHOD": "GET",
                "PATH_INFO": "/FOO/BAR",
                "POST": {"FOO": "BAZ", "XXX": "YYY"},
            },
            "slow_calls": [
                {
                    "type": "sql",
                    "start": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
                    "end": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
                    "subtype": "postgresql",
                    "parameters": ["QPARAM1", "QPARAM2", "QPARAMX"],
                    "statement": "QUERY",
                }
            ],
            "request_stats": {
                "main": 0.50779,
                "nosql": 0.01008,
                "nosql_calls": 17.0,
                "remote": 0.0,
                "remote_calls": 0.0,
                "custom": 0.0,
                "custom_calls": 0.0,
                "sql": 0.42423,
                "sql_calls": 1.0,
                "tmpl": 0.0,
                "tmpl_calls": 0.0,
            },
            "traceback": [
                {
                    "cline": "return foo_bar_baz(1,2,3)",
                    "file": "somedir/somefile.py",
                    "fn": "somefunction",
                    "line": 454,
                    "vars": [
                        ["a_list", ["1", "2", "4", "5", "6"]],
                        ["b", {1: "2", "ccc": "ddd", "1": "a"}],
                        ["obj", "<object object at 0x7f0030853dc0>"],
                    ],
                },
                {
                    "cline": "OMG ValueError happened",
                    "file": "",
                    "fn": "",
                    "line": "",
                    "vars": [],
                },
            ],
        }
    ],
}

PYTHON_PAYLOAD_0_5 = {
    "client": "your-client-name-python",
    "language": "python",
    "view_name": "views/foo:bar",
    "server": "servername/instancename",
    "priority": 5,
    "error": "OMG ValueError happened test",
    "occurences": 1,
    "http_status": 500,
    "username": "USER",
    "url": "HTTP://SOMEURL",
    "ip": "127.0.0.1",
    "start_time": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
    "end_time": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
    "user_agent": "BROWSER_AGENT",
    "message": "arbitrary text that will get attached to your report",
    "request_id": "SOME_UUID",
    "request": {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/FOO/BAR",
        "POST": {"FOO": "BAZ", "XXX": "YYY"},
    },
    "slow_calls": [
        {
            "type": "sql",
            "start": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
            "end": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
            "subtype": "postgresql",
            "parameters": ["QPARAM1", "QPARAM2", "QPARAMX"],
            "statement": "QUERY",
        }
    ],
    "request_stats": {
        "main": 0.50779,
        "nosql": 0.01008,
        "nosql_calls": 17.0,
        "remote": 0.0,
        "remote_calls": 0.0,
        "custom": 0.0,
        "custom_calls": 0.0,
        "sql": 0.42423,
        "sql_calls": 1.0,
        "tmpl": 0.0,
        "tmpl_calls": 0.0,
    },
    "traceback": [
        {
            "cline": "return foo_bar_baz(1,2,3)",
            "file": "somedir/somefile.py",
            "fn": "somefunction",
            "line": 454,
            "vars": [
                ["a_list", ["1", "2", "4", "5", "6"]],
                ["b", {1: "2", "ccc": "ddd", "1": "a"}],
                ["obj", "<object object at 0x7f0030853dc0>"],
            ],
        },
        {
            "cline": "OMG ValueError happened",
            "file": "",
            "fn": "",
            "line": "",
            "vars": [],
        },
    ],
}

PHP_PAYLOAD = {
    "client": "php",
    "error": 'Nie mo\u017cna ustali\u0107 \u017c\u0105dania "feed.xml".',
    "error_type": "",
    "http_status": 404,
    "language": "unknown",
    "priority": 1,
    "report_details": [
        {
            "end_time": None,
            "group_string": None,
            "ip": None,
            "message": "exception 'CHttpException' with message 'Nie mo\u017cna ustali\u0107 \u017c\u0105dania \"feed.xml\".' in /home/dobryslownik/www/sites/dobryslownik/vendor/yiisoft/yii/framework/web/CWebApplication.php:286\nStack trace:\n#0 /home/dobryslownik/www/sites/dobryslownik/common/components/WebApplication.php(34): CWebApplication->runController('feed.xml')\n#1 /home/dobryslownik/www/sites/dobryslownik/vendor/yiisoft/yii/framework/web/CWebApplication.php(141): WebApplication->runController('feed.xml')\n#2 /home/dobryslownik/www/sites/dobryslownik/vendor/yiisoft/yii/framework/base/CApplication.php(180): CWebApplication->processRequest()\n#3 /home/dobryslownik/www/sites/dobryslownik/frontend/www/index.php(23): CApplication->run()\n#4 {main}",
            "occurences": 1,
            "request": {
                "COOKIES": [],
                "FILES": [],
                "GET": [],
                "POST": [],
                "REQUEST_METHOD": None,
                "SERVER": {
                    "DOCUMENT_ROOT": "/home/dobryslownik/www/sites/dobryslownik/frontend/www/",
                    "GATEWAY_INTERFACE": "CGI/1.1",
                    "HTTPS": "on",
                    "HTTP_ACCEPT": "*/*",
                    "HTTP_ACCEPT_ENCODING": "gzip, deflate",
                    "HTTP_ACCEPT_LANGUAGE": "pl-PL",
                    "HTTP_CONNECTION": "close",
                    "HTTP_HOST": "dobryslownik.pl",
                    "HTTP_IF_MODIFIED_SINCE": "Wed, 30 Jul 2014 18:26:32 GMT",
                    "HTTP_IF_NONE_MATCH": '"45de3-2a3-4ff6d4b9fbe7f"',
                    "HTTP_USER_AGENT": "Apple-PubSub/28",
                    "HTTP_X_FORWARDED_FOR": "195.150.190.186",
                    "HTTP_X_FORWARDED_PROTO": "https",
                    "PATH": "/bin:/usr/bin:/usr/ucb:/usr/bsd:/usr/local/bin",
                    "PHP_SELF": "/index.php",
                    "QUERY_STRING": "",
                    "REDIRECT_HTTPS": "on",
                    "REDIRECT_STATUS": "200",
                    "REDIRECT_UNIQUE_ID": "VFAhZQoCaXIAAAkd414AAAAC",
                    "REDIRECT_URL": "/feed.xml",
                    "REMOTE_ADDR": "195.150.190.186",
                    "REMOTE_PORT": "41728",
                    "REQUEST_METHOD": "GET",
                    "REQUEST_TIME": 1414537573,
                    "REQUEST_TIME_FLOAT": 1414537573.32,
                    "REQUEST_URI": "/feed.xml",
                    "SCRIPT_FILENAME": "/home/dobryslownik/www/sites/dobryslownik/frontend/www/index.php",
                    "SCRIPT_NAME": "/index.php",
                    "SERVER_ADDR": "10.2.105.114",
                    "SERVER_ADMIN": "[no address given]",
                    "SERVER_NAME": "dobryslownik.pl",
                    "SERVER_SIGNATURE": "",
                    "SERVER_SOFTWARE": "Apache/2.2.22 (Ubuntu) PHP/5.4.17",
                    "UNIQUE_ID": "VFAg4AoCaXIAAAkd40UAAAAC",
                },
                "SESSION": [],
            },
            "request_id": "VFAg4AoCaXIAAAkd40UAAAAC",
            "request_stats": {
                "custom": 0,
                "custom_calls": 0,
                "main": 0,
                "nosql": 0.0,
                "nosql_calls": 0.0,
                "remote": 0.0,
                "remote_calls": 0.0,
                "sql": 0.0,
                "sql_calls": 0.0,
                "tmpl": 0.0,
                "tmpl_calls": 0.0,
                "unknown": 0.0,
            },
            "slow_calls": [],
            "start_time": None,
            "frameinfo": [
                {
                    "cline": None,
                    "file": "/home/dobryslownik/www/sites/dobryslownik/common/components/WebApplication.php",
                    "fn": "CWebApplication->runController",
                    "line": 34,
                    "vars": ["feed.xml"],
                },
                {
                    "cline": None,
                    "file": "/home/dobryslownik/www/sites/dobryslownik/vendor/yiisoft/yii/framework/web/CWebApplication.php",
                    "fn": "WebApplication->runController",
                    "line": 141,
                    "vars": ["feed.xml"],
                },
                {
                    "cline": None,
                    "file": "/home/dobryslownik/www/sites/dobryslownik/vendor/yiisoft/yii/framework/base/CApplication.php",
                    "fn": "CWebApplication->processRequest",
                    "line": 180,
                    "vars": [],
                },
                {
                    "cline": None,
                    "file": "/home/dobryslownik/www/sites/dobryslownik/frontend/www/index.php",
                    "fn": "CApplication->run",
                    "line": 23,
                    "vars": [],
                },
            ],
            "url": "https://dobryslownik.pl/feed.xml",
            "user_agent": "magpie-crawler/1.1 (U; Linux amd64; en-GB; +http://www.brandwatch.net)",
            "username": "guest",
        }
    ],
    "server": "unknown",
    "traceback": "",
    "view_name": "",
}

JS_PAYLOAD = {
    "client": "javascript",
    "language": "javascript",
    "error_type": "ReferenceError: non_existant_var is not defined",
    "occurences": 1,
    "priority": 5,
    "server": "jstest.appenlight",
    "http_status": 500,
    "report_details": [
        {
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
            "start_time": "2014-10-29T19:59:30.589Z",
            "frameinfo": [
                {
                    "cline": "",
                    "file": "http://demo.appenlight.com/#",
                    "fn": "HTMLAnchorElement.onclick",
                    "line": 79,
                    "vars": [],
                },
                {
                    "cline": "",
                    "file": "http://demo.appenlight.com/static/js/demo.js",
                    "fn": "test_error",
                    "line": 7,
                    "vars": [],
                },
                {
                    "cline": "ReferenceError: non_existant_var is not defined",
                    "file": "http://demo.appenlight.com/static/js/demo.js",
                    "fn": "something",
                    "line": 2,
                    "vars": [],
                },
            ],
            "url": "http://demo.appenlight.com/#",
            "server": "jstest.appenlight",
            "username": "i_am_mario",
            "ip": "127.0.0.1",
            "request_id": "0.01984176435507834",
        }
    ],
}

AIRBRAKE_RUBY_EXAMPLE = """
<?xml version="1.0" ?>
<notice version="2.4">
    <api-key>APPENLIGHT_API_KEY</api-key>
    <notifier>
        <name>Airbrake Notifier</name>
        <version>3.1.7</version>
        <url>https://github.com/airbrake/airbrake</url>
    </notifier>
    <error>
        <class>NameError</class>
        <message>NameError: undefined local variable or method `sdfdfdf' for #&lt;#&lt;Class:0x000000039a8b90&gt;:0x00000002c53df0&gt;</message>
        <backtrace>
            <line file="[PROJECT_ROOT]/app/views/welcome/index.html.erb" method="_app_views_welcome_index_html_erb___2570061166873166679_31748940" number="3"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/template.rb" method="block in render" number="145"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/notifications.rb" method="instrument" number="125"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/template.rb" method="render" number="143"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/template_renderer.rb" method="block (2 levels) in render_template" number="47"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/abstract_renderer.rb" method="block in instrument" number="38"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/notifications.rb" method="block in instrument" number="123"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/notifications/instrumenter.rb" method="instrument" number="20"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/notifications.rb" method="instrument" number="123"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/abstract_renderer.rb" method="instrument" number="38"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/template_renderer.rb" method="block in render_template" number="46"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/template_renderer.rb" method="render_with_layout" number="54"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/template_renderer.rb" method="render_template" number="45"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/template_renderer.rb" method="render" number="18"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/renderer.rb" method="render_template" number="36"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_view/renderer/renderer.rb" method="render" number="17"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/abstract_controller/rendering.rb" method="_render_template" number="110"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/streaming.rb" method="_render_template" number="225"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/abstract_controller/rendering.rb" method="render_to_body" number="103"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/renderers.rb" method="render_to_body" number="28"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/compatibility.rb" method="render_to_body" number="50"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/abstract_controller/rendering.rb" method="render" number="88"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/rendering.rb" method="render" number="16"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/instrumentation.rb" method="block (2 levels) in render" number="40"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/core_ext/benchmark.rb" method="block in ms" number="5"/>
            <line file="/home/ergo/.rbenv/versions/1.9.3-p327/lib/ruby/1.9.1/benchmark.rb" method="realtime" number="295"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/core_ext/benchmark.rb" method="ms" number="5"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/instrumentation.rb" method="block in render" number="40"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/instrumentation.rb" method="cleanup_view_runtime" number="83"/>
            <line file="[GEM_ROOT]/gems/activerecord-3.2.11/lib/active_record/railties/controller_runtime.rb" method="cleanup_view_runtime" number="24"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/instrumentation.rb" method="render" number="39"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/implicit_render.rb" method="default_render" number="10"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/implicit_render.rb" method="send_action" number="5"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/abstract_controller/base.rb" method="process_action" number="167"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/rendering.rb" method="process_action" number="10"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/abstract_controller/callbacks.rb" method="block in process_action" number="18"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/callbacks.rb" method="_run__2035827918079922105__process_action__2488436794202946797__callbacks" number="414"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/callbacks.rb" method="__run_callback" number="405"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/callbacks.rb" method="_run_process_action_callbacks" number="385"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/callbacks.rb" method="run_callbacks" number="81"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/abstract_controller/callbacks.rb" method="process_action" number="17"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/rescue.rb" method="process_action" number="29"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/instrumentation.rb" method="block in process_action" number="30"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/notifications.rb" method="block in instrument" number="123"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/notifications/instrumenter.rb" method="instrument" number="20"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/notifications.rb" method="instrument" number="123"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/instrumentation.rb" method="process_action" number="29"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/params_wrapper.rb" method="process_action" number="207"/>
            <line file="[GEM_ROOT]/gems/activerecord-3.2.11/lib/active_record/railties/controller_runtime.rb" method="process_action" number="18"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/abstract_controller/base.rb" method="process" number="121"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/abstract_controller/rendering.rb" method="process" number="45"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal.rb" method="dispatch" number="203"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal/rack_delegation.rb" method="dispatch" number="14"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_controller/metal.rb" method="block in action" number="246"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/routing/route_set.rb" method="call" number="73"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/routing/route_set.rb" method="dispatch" number="73"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/routing/route_set.rb" method="call" number="36"/>
            <line file="[GEM_ROOT]/gems/journey-1.0.4/lib/journey/router.rb" method="block in call" number="68"/>
            <line file="[GEM_ROOT]/gems/journey-1.0.4/lib/journey/router.rb" method="each" number="56"/>
            <line file="[GEM_ROOT]/gems/journey-1.0.4/lib/journey/router.rb" method="call" number="56"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/routing/route_set.rb" method="call" number="601"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/best_standards_support.rb" method="call" number="17"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/etag.rb" method="call" number="23"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/conditionalget.rb" method="call" number="25"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/head.rb" method="call" number="14"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/params_parser.rb" method="call" number="21"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/flash.rb" method="call" number="242"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/session/abstract/id.rb" method="context" number="210"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/session/abstract/id.rb" method="call" number="205"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/cookies.rb" method="call" number="341"/>
            <line file="[GEM_ROOT]/gems/activerecord-3.2.11/lib/active_record/query_cache.rb" method="call" number="64"/>
            <line file="[GEM_ROOT]/gems/activerecord-3.2.11/lib/active_record/connection_adapters/abstract/connection_pool.rb" method="call" number="479"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/callbacks.rb" method="block in call" number="28"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/callbacks.rb" method="_run__3791281566140176909__call__1380026543027572563__callbacks" number="405"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/callbacks.rb" method="__run_callback" number="405"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/callbacks.rb" method="_run_call_callbacks" number="385"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/callbacks.rb" method="run_callbacks" number="81"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/callbacks.rb" method="call" number="27"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/reloader.rb" method="call" number="65"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/remote_ip.rb" method="call" number="31"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/debug_exceptions.rb" method="call" number="16"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/show_exceptions.rb" method="call" number="56"/>
            <line file="[GEM_ROOT]/gems/railties-3.2.11/lib/rails/rack/logger.rb" method="call_app" number="32"/>
            <line file="[GEM_ROOT]/gems/railties-3.2.11/lib/rails/rack/logger.rb" method="block in call" number="16"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/tagged_logging.rb" method="tagged" number="22"/>
            <line file="[GEM_ROOT]/gems/railties-3.2.11/lib/rails/rack/logger.rb" method="call" number="16"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/request_id.rb" method="call" number="22"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/methodoverride.rb" method="call" number="21"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/runtime.rb" method="call" number="17"/>
            <line file="[GEM_ROOT]/gems/activesupport-3.2.11/lib/active_support/cache/strategy/local_cache.rb" method="call" number="72"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/lock.rb" method="call" number="15"/>
            <line file="[GEM_ROOT]/gems/actionpack-3.2.11/lib/action_dispatch/middleware/static.rb" method="call" number="62"/>
            <line file="[GEM_ROOT]/gems/railties-3.2.11/lib/rails/engine.rb" method="call" number="479"/>
            <line file="[GEM_ROOT]/gems/railties-3.2.11/lib/rails/application.rb" method="call" number="223"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/content_length.rb" method="call" number="14"/>
            <line file="[GEM_ROOT]/gems/railties-3.2.11/lib/rails/rack/log_tailer.rb" method="call" number="17"/>
            <line file="[GEM_ROOT]/gems/rack-1.4.4/lib/rack/handler/webrick.rb" method="service" number="59"/>
            <line file="/home/ergo/.rbenv/versions/1.9.3-p327/lib/ruby/1.9.1/webrick/httpserver.rb" method="service" number="138"/>
            <line file="/home/ergo/.rbenv/versions/1.9.3-p327/lib/ruby/1.9.1/webrick/httpserver.rb" method="run" number="94"/>
            <line file="/home/ergo/.rbenv/versions/1.9.3-p327/lib/ruby/1.9.1/webrick/server.rb" method="block in start_thread" number="191"/>
        </backtrace>
    </error>
    <request>
        <url>http://0.0.0.0:3000/welcome/index?test=1234</url>
        <component>welcome</component>
        <action>index</action>
        <params>
            <var key="test">1234</var>
            <var key="controller">welcome</var>
            <var key="action">index</var>
        </params>
        <session>
            <var key="session_id">4706af9678e4b94f2bb66e1d85ced382</var>
            <var key="_csrf_token">h9R7MuRtnNX6ZDK6vI1pIJV3dYYtlEx1mPw/nzyIVTA=</var>
        </session>
        <cgi-data>
            <var key="GATEWAY_INTERFACE">CGI/1.1</var>
            <var key="PATH_INFO">/welcome/index</var>
            <var key="QUERY_STRING">test=1234</var>
            <var key="REMOTE_ADDR">127.0.0.1</var>
            <var key="REMOTE_HOST">localhost</var>
            <var key="REQUEST_METHOD">GET</var>
            <var key="REQUEST_URI">http://0.0.0.0:3000/welcome/index?test=1234</var>
            <var key="SCRIPT_NAME"/>
            <var key="SERVER_NAME">0.0.0.0</var>
            <var key="SERVER_PORT">3000</var>
            <var key="SERVER_PROTOCOL">HTTP/1.1</var>
            <var key="SERVER_SOFTWARE">WEBrick/1.3.1 (Ruby/1.9.3/2012-11-10)</var>
            <var key="HTTP_HOST">0.0.0.0:3000</var>
            <var key="HTTP_CONNECTION">keep-alive</var>
            <var key="HTTP_CACHE_CONTROL">max-age=0</var>
            <var key="HTTP_ACCEPT">text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8</var>
            <var key="HTTP_USER_AGENT">Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17</var>
            <var key="HTTP_DNT">1</var>
            <var key="HTTP_ACCEPT_ENCODING">gzip,deflate,sdch</var>
            <var key="HTTP_ACCEPT_LANGUAGE">pl,en-US;q=0.8,en;q=0.6</var>
            <var key="HTTP_ACCEPT_CHARSET">ISO-8859-1,utf-8;q=0.7,*;q=0.3</var>
            <var key="HTTP_COOKIE">_rails_app_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFRkkiJTQ3MDZhZjk2NzhlNGI5NGYyYmI2NmUxZDg1Y2VkMzgyBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMWg5UjdNdVJ0bk5YNlpESzZ2STFwSUpWM2RZWXRsRXgxbVB3L256eUlWVEE9BjsARg%3D%3D--08a5940133e1c7f7ca58ed5154e3a8e7acae337a</var>
            <var key="rack.version">[&quot;1&quot;, &quot;1&quot;]</var>
            <var key="rack.input">#&lt;StringIO:0x00000003b6ca08&gt;</var>
            <var key="rack.errors">#&lt;IO:0x00000001e76228&gt;</var>
            <var key="rack.multithread">false</var>
            <var key="rack.multiprocess">false</var>
            <var key="rack.run_once">false</var>
            <var key="rack.url_scheme">http</var>
            <var key="HTTP_VERSION">HTTP/1.1</var>
            <var key="REQUEST_PATH">/welcome/index</var>
            <var key="ORIGINAL_FULLPATH">/welcome/index?test=1234</var>
            <var key="action_dispatch.routes">#&lt;ActionDispatch::Routing::RouteSet:0x00000002b31648&gt;</var>
            <var key="action_dispatch.parameter_filter">[&quot;password&quot;]</var>
            <var key="action_dispatch.show_exceptions">true</var>
            <var key="action_dispatch.show_detailed_exceptions">true</var>
            <var key="action_dispatch.logger">#&lt;ActiveSupport::TaggedLogging:0x00000002ae79d0&gt;</var>
            <var key="action_dispatch.backtrace_cleaner">#&lt;Rails::BacktraceCleaner:0x000000029a7250&gt;</var>
            <var key="action_dispatch.request_id">c11b2267f3ad8b00a1768cae35559fa1</var>
            <var key="action_dispatch.remote_ip">127.0.0.1</var>
            <var key="rack.session">
                <var key="session_id">4706af9678e4b94f2bb66e1d85ced382</var>
                <var key="_csrf_token">h9R7MuRtnNX6ZDK6vI1pIJV3dYYtlEx1mPw/nzyIVTA=</var>
            </var>
            <var key="rack.session.options">
                <var key="path">/</var>
                <var key="domain"/>
                <var key="expire_after"/>
                <var key="secure">false</var>
                <var key="httponly">true</var>
                <var key="defer">false</var>
                <var key="renew">false</var>
                <var key="secret">e96386a74a0c95f5c8eeaf95e47d14962973a0ff9e9d32841703559423b1</var>
                <var key="coder">#&lt;Rack::Session::Cookie::Base64::Marshal:0x00000002daf528&gt;</var>
                <var key="id">4706af9678e4b94f2bb66e1d85ced382</var>
            </var>
            <var key="rack.request.cookie_hash">
                <var key="_rails_app_session">BAh7B0kiD3Nlc3Npb25faWQGOgZFRkkiJTQ3MDZhZjk2NzhlNGI5NGYyYmI2NmUxZDg1Y2VkMzgyBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMWg5UjdNdVJ0bk5YNlpESzZ2STFwSUpWM2RZWXRsRXgxbVB3L256eUlWVEE9BjsARg==--08a5940133e1c7f7ca58ed5154e3a8e7acae337a</var>
            </var>
            <var key="rack.request.cookie_string">_rails_app_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFRkkiJTQ3MDZhZjk2NzhlNGI5NGYyYmI2NmUxZDg1Y2VkMzgyBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMWg5UjdNdVJ0bk5YNlpESzZ2STFwSUpWM2RZWXRsRXgxbVB3L256eUlWVEE9BjsARg%3D%3D--08a5940133e1c7f7ca58ed5154e3a8e7acae337a</var>
            <var key="action_dispatch.cookies">#&lt;ActionDispatch::Cookies::CookieJar:0x00000002c51e38&gt;</var>
            <var key="action_dispatch.request.unsigned_session_cookie">
                <var key="session_id">4706af9678e4b94f2bb66e1d85ced382</var>
                <var key="_csrf_token">h9R7MuRtnNX6ZDK6vI1pIJV3dYYtlEx1mPw/nzyIVTA=</var>
            </var>
            <var key="action_dispatch.request.path_parameters">
                <var key="controller">welcome</var>
                <var key="action">index</var>
            </var>
            <var key="action_controller.instance">#&lt;WelcomeController:0x00000002c4f020&gt;</var>
            <var key="action_dispatch.request.content_type"/>
            <var key="action_dispatch.request.request_parameters"/>
            <var key="rack.request.query_string">test=1234</var>
            <var key="rack.request.query_hash">
                <var key="test">1234</var>
            </var>
            <var key="action_dispatch.request.query_parameters">
                <var key="test">1234</var>
            </var>
            <var key="action_dispatch.request.parameters">
                <var key="test">1234</var>
                <var key="controller">welcome</var>
                <var key="action">index</var>
            </var>
            <var key="action_dispatch.request.formats">[&quot;text/html&quot;]</var>
        </cgi-data>
    </request>
    <server-environment>
        <project-root>/home/ergo/workspace/rails_app</project-root>
        <environment-name>development</environment-name>
        <hostname>ergo-desktop</hostname>
    </server-environment>
    <framework>Rails: 3.2.11</framework>
</notice>
""".replace(
    "\n", ""
).replace(
    "  ", ""
)

AIRBRAKE_EXAMPLE_SHORT = """
<?xml version="1.0" encoding="UTF-8"?>
<notice version="2.3">
  <api-key>76fdb93ab2cf276ec080671a8b3d3866</api-key>
  <notifier>
    <name>Airbrake Notifier</name>
    <version>3.1.6</version>
    <url>http://api.airbrake.io</url>
  </notifier>
  <error>
    <class>RuntimeError</class>
    <message>RuntimeError: I've made a huge mistake</message>
    <backtrace>
      <line method="public" file="/testapp/app/models/user.rb" number="53"/>
      <line method="index" file="/testapp/app/controllers/users_controller.rb" number="14"/>
    </backtrace>
  </error>
  <request>
    <url>http://example.com</url>
    <component/>
    <action/>
    <cgi-data>
      <var key="SERVER_NAME">example.org</var>
      <var key="HTTP_USER_AGENT">Mozilla</var>
    </cgi-data>
  </request>
  <server-environment>
    <project-root>/testapp</project-root>
    <environment-name>production</environment-name>
    <app-version>1.0.0</app-version>
  </server-environment>
</notice>
""".replace(
    "\n", ""
).replace(
    "  ", ""
)

SENTRY_PYTHON_PAYLOAD_7 = {
    "culprit": "djangoapp.views in error",
    "event_id": "9fae652c8c1c4d6a8eee09260f613a98",
    "exception": {
        "values": [
            {
                "module": "exceptions",
                "stacktrace": {
                    "frames": [
                        {
                            "abs_path": "/home/ergo/venvs/appenlight/local/lib/python2.7/site-packages/django/core/handlers/base.py",
                            "context_line": "response = wrapped_callback(request, *callback_args, **callback_kwargs)",
                            "filename": "django/core/handlers/base.py",
                            "function": "get_response",
                            "in_app": False,
                            "lineno": 111,
                            "module": "django.core.handlers.base",
                            "post_context": [
                                "                except Exception as e:",
                                "                    # If the view raised an exception, run it through exception",
                                "                    # middleware, and if the exception middleware returns a",
                                "                    # response, use that. Otherwise, reraise the exception.",
                                "                    for middleware_method in self._exception_middleware:",
                            ],
                            "pre_context": [
                                "                        break",
                                "",
                                "            if response is None:",
                                "                wrapped_callback = self.make_view_atomic(callback)",
                                "                try:",
                            ],
                            "vars": {
                                "callback": "<function error from djangoapp.views at 0x7fe7c9f2cb90>",
                                "callback_args": [],
                                "callback_kwargs": {},
                                "e": "Exception(u'test 500 \\u0142\\xf3\\u201c\\u0107\\u201c\\u0107\\u017c\\u0105',)",
                                "middleware_method": "<bound method MessageMiddleware.process_request of <django.contrib.messages.middleware.MessageMiddleware object at 0x7fe7c8b0c950>>",
                                "request": "<WSGIRequest at 0x140633490316304>",
                                "resolver": "<RegexURLResolver 'djangoapp.urls' (None:None) ^/>",
                                "resolver_match": "ResolverMatch(func=<function error at 0x7fe7c9f2cb90>, args=(), kwargs={}, url_name='error', app_name='None', namespace='')",
                                "response": None,
                                "self": "<django.core.handlers.wsgi.WSGIHandler object at 0x7fe7cf75a790>",
                                "urlconf": "'djangoapp.urls'",
                                "wrapped_callback": "<function error from djangoapp.views at 0x7fe7c9f2cb90>",
                            },
                        },
                        {
                            "abs_path": "/home/ergo/IdeaProjects/django_raven/djangoapp/views.py",
                            "context_line": "raise Exception(u'test 500 \u0142\xf3\u201c\u0107\u201c\u0107\u017c\u0105')",
                            "filename": "djangoapp/views.py",
                            "function": "error",
                            "in_app": False,
                            "lineno": 84,
                            "module": "djangoapp.views",
                            "post_context": [
                                "",
                                "",
                                "def notfound(request):",
                                "    raise Http404('404 appenlight exception test')",
                                "",
                            ],
                            "pre_context": [
                                "    c.execute(\"INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)\")",
                                "    c.execute(\"INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)\")",
                                "    conn.commit()",
                                "    c.close()",
                                "    request.POST.get('DUPA')",
                            ],
                            "vars": {
                                "c": "<sqlite3.Cursor object at 0x7fe7c82af8f0>",
                                "conn": "<sqlite3.Connection object at 0x7fe7c8b23bf8>",
                                "request": "<WSGIRequest at 0x140633490316304>",
                            },
                        },
                    ]
                },
                "type": "Exception",
                "value": "test 500 \u0142\xf3\u201c\u0107\u201c\u0107\u017c\u0105",
            }
        ]
    },
    "extra": {"sys.argv": ["'manage.py'", "'runserver'"]},
    "level": 40,
    "message": "Exception: test 500 \u0142\xf3\u201c\u0107\u201c\u0107\u017c\u0105",
    "modules": {"django": "1.7.1", "python": "2.7.6", "raven": "5.9.2"},
    "platform": "python",
    "project": "sentry",
    "release": "test",
    "request": {
        "cookies": {"appenlight": "X"},
        "data": None,
        "env": {
            "REMOTE_ADDR": "127.0.0.1",
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "8000",
        },
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8,pl;q=0.6",
            "Connection": "keep-alive",
            "Content-Length": "",
            "Content-Type": "text/plain",
            "Cookie": "appenlight=X",
            "Dnt": "1",
            "Host": "127.0.0.1:8000",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
        },
        "method": "GET",
        "query_string": "",
        "url": "http://127.0.0.1:8000/error",
    },
    "server_name": "ergo-virtual-machine",
    "tags": {"site": "example.com"},
    "time_spent": None,
    "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
}


SENTRY_JS_PAYLOAD_7 = {
    "project": "sentry",
    "logger": "javascript",
    "platform": "javascript",
    "request": {
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
        },
        "url": "http://localhost:6543/test/js_error#/",
    },
    "exception": {
        "values": [
            {
                "type": "ReferenceError",
                "value": "fateqtwetew is not defined",
                "stacktrace": {
                    "frames": [
                        {
                            "filename": "https://cdn.ravenjs.com/2.0.0/angular/raven.min.js",
                            "lineno": 1,
                            "colno": 4466,
                            "function": "c",
                            "in_app": False,
                        },
                        {
                            "filename": "http://localhost:6543/test/js_error",
                            "lineno": 47,
                            "colno": 19,
                            "function": "?",
                            "in_app": True,
                        },
                    ]
                },
            }
        ]
    },
    "culprit": "http://localhost:6543/test/js_error",
    "message": "ReferenceError: fateqtwetew is not defined",
    "extra": {"session:duration": 5009},
    "event_id": "2bf514aaf0e94f35a8f435a0d29a888b",
}

SENTRY_JS_PAYLOAD_7_2 = {
    "project": "sentry",
    "logger": "javascript",
    "platform": "javascript",
    "request": {
        "headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
        },
        "url": "http://localhost:6543/#/report/927/9558",
    },
    "exception": {
        "values": [
            {
                "type": "Error",
                "value": "[$injector:modulerr] http://errors.angularjs.org/1.5.0-rc.0/$injector/modulerr?p0=appenlight&p1=Erro…",
                "stacktrace": {
                    "frames": [
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1647,
                            "colno": 112,
                            "function": "?",
                            "in_app": True,
                        },
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1363,
                            "colno": 41,
                            "function": "be",
                            "in_app": True,
                        },
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1364,
                            "colno": 225,
                            "function": "zc",
                            "in_app": True,
                        },
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1363,
                            "colno": 421,
                            "function": "c",
                            "in_app": True,
                        },
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1386,
                            "colno": 360,
                            "function": "fb",
                            "in_app": True,
                        },
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1383,
                            "colno": 49,
                            "function": "g",
                            "in_app": True,
                        },
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1351,
                            "colno": 344,
                            "function": "n",
                            "in_app": True,
                        },
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1383,
                            "colno": 475,
                            "function": "?",
                            "in_app": True,
                        },
                        {
                            "filename": "http://localhost:6543/static/js/appenlight.js?rev=752",
                            "lineno": 1350,
                            "colno": 421,
                            "function": "?",
                            "in_app": True,
                        },
                    ]
                },
            }
        ]
    },
    "culprit": "http://localhost:6543/static/js/appenlight.js?rev=752",
    "message": "Error: [$injector:modulerr] http://errors.angularjs.org/1.5.0-rc.0/$injector/modulerr?p0=appenlight&…",
    "extra": {"session:duration": 330},
    "event_id": "c50b5b6a13994f54b1d8da0c2e0e767a",
}

SENTRY_LOG_PAYLOAD_7 = {
    "project": "sentry",
    "sentry.interfaces.Message": {"message": "TEST from django logging", "params": []},
    "server_name": "ergo-virtual-machine",
    "culprit": "testlogger in index",
    "extra": {
        "thread": 139723601139456,
        "process": 24645,
        "sys.argv": ["'manage.py'", "'runserver'"],
        "price": 6,
        "threadName": "'Thread-1'",
        "filename": "'views.py'",
        "processName": "'MainProcess'",
        "tag": "'extra'",
        "dupa": True,
        "lineno": 22,
        "asctime": "'2016-01-18 05:24:29,001'",
        "pathname": "'/home/ergo/IdeaProjects/django_raven/djangoapp/views.py'",
    },
    "event_id": "9a6172f2e6d2444582f83a6c333d9cfb",
    "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "tags": {"site": "example.com"},
    "modules": {"python": "2.7.6", "raven": "5.9.2", "django": "1.7.1"},
    "time_spent": None,
    "platform": "python",
    "release": "test",
    "logger": "testlogger",
    "level": 50,
    "message": "TEST from django logging",
}

METRICS_PAYLOAD = {
    "namespace": "some.monitor",
    "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S.0"),
    "server_name": "server.name",
    "tags": [["usage_foo", 15.5], ["usage_bar", 63]],
}


SENTRY_PYTHON_ENCODED = b'x\x9c\xedXmo\xdbF\x12\xfe+\x0b\xdd\x07I9\x89/z\x97[\x05p\x1d5\x0ej\'\x81,\xa7\xed\xd59bE\x8d$V|\xcb\xeeR\x96k\xf8\xbf\xdf\xcc.II\xb6\xdc\xf4\xd2\x16\xb8\x03\xa2 \x06\xb9\xdc\x9d\x9dy\xe6\x99y\x96\xbc\xaf\xa4"\xf9\x15|U9a\x15\t\xb1\x12w\x95\x06\xab\xc0\xd6\x87T\x05I\x8c\xc3\xf7\x95\r\x0f3\x90x\xf9\xcb}E*\xee\xaf\x95\xe0>\xe8G\x0b\xc1\xa3\xe2\xd1"\x8b\xfd|Me\t\xca\x13 \xd3$\x96@\x06\xf9Lz)W+zf\xaf\x92\x08l\x10\xcb\xc4\xde@\xbc\x91vz\xa7VI\xdc\xb2\xc3\xc4\xe7\xa1\x1d\x06\xb3b\xc4\xea\xdb2P\xd0LqO\xbe\x04i\xcf\x7f\xe51.\xf3\x13\x01\xf6\x8a\xc7\xf3\x10\x84\xb4g\\\x82\x95j\xbfS\x01\x9e\x9f\xc4\n\xb6\x14\xd0/\x15\xb6\xf7\x0b\x16\xac\xf0\x88\x05\x92\xbdMb8\xa15\xec\xd1\xefV\xf04\x85\xb9\x87\xbe\x843\xdc\x98\x8d\x98\x84paE|\r\xde&\x80[\x8f\xab$\n\xfcZ1\xa1~\xcc\n\x02y\xd4:\xfdJ7FO6\xab\t\xf8\x84X\xab\x06{Q\x0cy\\,%\xde\xef\x06\xd6\xb74tt[\x9386.\xf2\xc7\xb8d\x18\xe6G\xc2&\x91\xea\x00\x9c\xc7\xeb\xff\xc1\xce\x92(\ry\x10\x13Vj\x05\x8c\xa2EoU&b\x98k\xc4X\x8d3?\x89"\xb4\x0cB$\xa2n=\xb6\xf2Ga\xc6y\x81\x0cb\xe4S\xecC\x89e\x83\xa9\xbb\x14\xa4\xf5}\xce\xa5)\xde\xd5O\x8cw\xdf\x7f\xf7\xe19DuZb\xa4"BZ\x98\xb2<=\xe2y:\xfa\r\x17R3\x96x[)\xf1\xa9eU\x85p\xb3\xae\xe3\xb0\x9b\x9b\xccq;\xad\x9b\x9b\xed\xa2\x8d\xd7-\xc7\xf5\xf5\x90\xd3\x7fr\xe7\xb8\xfd\xfc\xae[m\xe8D\x1cd\x8b\xe0\xa5M\x11\x88$\xdc\x80\xf0"\xae|\xcd\xfdI>rI\x035\xaa\x98\x91\xe14\xd2\xc0\xa2(\xa4\xa5qm0\xb23\xaa\xd5\x1b\xccd{t\xff\xd0`\x99\x08uL\xa3bN\x9a\xea{9\xa2\xed\xf4\x15\x96\x8a\xbe\xd5N\x15\x89\xf0\x02\x89\xd5\x18\xcfA\xc0\x1c\xbdX\xf0P\x02>\x8e\x829V\x10\x9a\x07/\x02,8zV\xf9v\x96d\xf1\x9c\x99\x01v\tRb\xe5]\x963-\xec\x17\xb8\x03\xd9\xd3De\xc9\x82}kB\xb0\x88\\"\x98Y\x91Y$\xad\xdd\x06\xd6\x13C,\x99Q\xdfa\\1g\xdb_\xb4{\xdd\xb6\x03}\x7f\xe8\xbc|I\xaeS\xc9iwJ\xdbh\xa4(y\xebV.\x03\xeb\xc7\xab\xd7o\xce\xcd\xc8ScC\xd7\x1f\xf6\xba\xceK\x03\x83vU\x9b\xa3E\x93\xdcu=\xdbm\x0f\x07}\xb75p;\xbdA\xabc\x16\x14\xc9\xd4+\x8a\xb6f\x08\xcf\x16"\x89\xd8\xa3\x9c\xed\x07\xe1\xf7\x06\x83\xce@\x9by\\\xdc\x7f\xd2\\\xc1&mf\x02K\xd8^O.\nB\xb1\xea\xce\x08\xd2DVYM\x97\x1e\xfd\xa9\xb3\x7f\xdb\x07q\xe5\x1d\x84\xea\xe1a\x8f&x\x1fga\x88#h\x01\x93\xa9\x13\xf0\xd8n\x85VD\xc9<\x0bu%\x1dM\x0fud\xdao\x11\x84@\xac\xdcM|\xbeu\x87A\x0cq\x823\xdd\xce\x10o\x83\xd8\xc3-\xf7\xc8\x9aw.\x8f\xe6\x91\xbd\xcf4V\xdd\xb2\x0b\xae\x96r\xe6\xcd\xee\xbc\x1d)kh7\xe7F\x9d\xc2\xfa\x9f\x97\xb0\xfd\xdfL\x00_\xd3\x82/m\xc0\x7f\xa1\xce\x1d\x95\x97\xc73\x9f\x91\xa6\xcfk\xe4\x7f\x9d\xca#\xa0\xfc\x8d\xda\xf6U]\xbe\xaa\xcbWu\xf9\xffQ\x97\xfe_\xa0.\x7f\xea\xd8\xfeDit\xae~Gbn\x13\xb1\xd6\xa5\x97\x8b\x87\'8\xaa\x8e]Bg\x9b\xd2~^?|\x0b\xb6\xe0g\nj7\x957o\xaf\xc6\x93){\xf3v\xfa\x8eI\x95\xf8k\xc9>\x9c^\\\x8f\xafX\xad\xdar\x9c^\xd3q\x9b\xd4w\xaa\xdf]\xff\x8c\x7f\'\xe7\xa7\xd3j\xc3u\x9cF\xbbk\xb9\x9d\xfaM\xa5\x94\x81\xbf\xc9j\x12\xc7\x16\xb5\xe1@\xd5\xf6\xb6\xf2\xc3D\xc2n \xc7\xdbz\xff\xeejj\xa1R\xd7\xaa\xaf\xae\xdf\x9fV\xeb\xcf\xbf\xe9\xd0\xff9,X\x9c\xa8\x05\xf5\xa0"e\xf5R\x82\x04\x0f0\xb9\xe7J\xa5\x1d\xa7S\xab\xe2\x1fSE\xd8^\xb1\x94J\xe1a\xd4\xd2\xabFe\x0ez\xbf\xafKG~\nQ\xef\xdb\xd6Y&dr\xa4u\xb4\x1c\xde\x99\x7fq\xeb@p\x0ew\xc1\x010\x15\x7f\xa4\xe3\xcd\x17\xfd>.<VSe;8^I\x8fYU\xd6\xcf\xa0\xfbG\xcb\xc7\xc0y\\\x0b\x8d\x14f\x8e\x83Zh\xc4\xcfh\xdf\xc1\xb5\x96A\xa3\x82X4\x1f)\nz9<P\xd8\xcaAhe\x8etT\xfa\xb3\x05\r\x7f\xf1\xbe\xf9\xae~\x16\xa6"PG\xc0cA\xdei\x8d\xa8\x08R\xe3\x02H*\xdd\xe6&\x10*\xe3a3\xe2\xfe\x8a\xb0\xd1\xdfV\x94\xe0\x9a0\xf2NZ\xd8\x126\x9a\xa3\xd5\x88\xc7(a\x88w\x95fUE\x16\x1b\x83\xd5\x8av\x02\xb0\xe4\x95\x17h\x15u\x17\xbd\xe1\x00\x86>\xcc\x16\xb3N\xdb\x1f\xce\x16=\x07\xda\xb3\xd6\x00|\x7f\x01\xd0=\xe4\x1623I\xd6\x01\x18\x96R\x9f\xcf\x84\xfe|Sq55\xb0\xf1\xd2\xcd\n\x89\x7fb\xdbn\xabo9\xf8\xcf=\x198\x8ec\x97\xd1\xad\x80\xa3\xc2\x1b\x1bg\x94\xeeX5/ ^\x9anE3N}B\xbfy\x81\x08e\x18\x89\xc6 n^_5 \xfe\xe6\xd3\xc8\xb1\x06\x8d4\xd4\x17\xbd\xbd\xd9\xe3\xd8O\xe6A\xbc\xd4\'\xee\xdf\x82\xb4\xc1\xb0HC\xae\x90Ur\x8e\xa7\x1a\x9c\xb9\xe38MZ\x03\xa4M\x1e\x06\x1b\xd8Y1I\xde*{\xa5\xa2\xb0\x81\xd9\t\x03\x9f\xd3\x02{K#\xff\xdc>\x1e\x8d\x8c#\xc3F\x10\xa1\xa7\xf6-\xcc\xd2\xc6\x0b\xfb\x85q\x93\xec^\xa7K\x81\xf16\xdf`\x12\xfcL@3/Mi`\xc3\x19\xafbU^\x9f\'\xa6\x88\x0f\xb13\xbe\x13\xf2\xf4\xac\xc0}\xa4W\x9c!\x1f\xa0I8\x8aD\xa3\x1f\xf1m\x13]\x19\xe9U\xd7\x98\xf9\xe6\xe9\x12\xcc\x16\x97\xc9oA\x18r\xbbk9\xac\xf6\x93\xeb~\xc3.\x828\xdb\xb2\xed\xa0\xe7\xf5:uv\x8a\x91\xc1\x8f0\xfb!Pv\xb7\xdd\xb7\xda=V\xfb\xe1|zy\xd1`a\xb0\x06\xf6\x1a\xfcuRgg+A\x8a\xd2%\x07[\xbd\x9ek\r;\xec\x8a/\xb8\x08\xf2U9\xd6:\xb3\xd3\xbc\xd04\xaa\xfa\xdc\xac\xa9\x82\xef:\x9a\x00\xd8\xec?\x8c\'\xde\xdb\xd3\xcb1\xcd\xd2o=+\x02\x01\xe7\xe4\xcf\xde\xbf\x9bL\xe9Y\x81\xc4d|\xf9n:\xf6N_\xbd\x9a\x1c@\xa5\xed"\xb6\xe2\xce\x93x\xbe3L\xd0\xcd\x9a+\xbe;3\xec\x8e\x90\xaf\xc7S\xbd&\xc4\x8a \xe8:N\xd9\x03\x0c;\xcd\x9b\x17M\xc5\xb7/C6-\x984Bjci\x7fL%kW\xac!\xce\xd2\xed%\x88\xc0\x93\xa9\xc1=\xdf\x18\x83G\xc1\x10\x11\xcd\xcc-\xe73\xa5\xe2Q\xaa\xb7q\\\x14\xb8n\xd3\xe9L\xdd\xdeI\xc79i\r\xffE\x93\xe8\x15m\xee\x8b,\x9a\xc9\'\xdfQ\x91\x89\xb0L\xc4]\xd1\x9f\xc2d\xb9\x04]hE\\\xbbc\xc1\xfef\xa8\x06\xad6b\xda\x1aZ\x9dn\xbf7\xdc\x01u\xbf\xd7Y\xb0]\xe9\n\xef\xd1j\xbe4\xbd\x91\x1e6\n\xb3\'\xf8\xe6\x96\xc1\x03E=\xcf\x04\xcf\xab\xab\x04[\x1f\xa7i\xd9t|5\xdd?F2r\x94\xb2\xb4\xd7\x8d\xb1by\x16*s\xb0\xd9\x0f\xcc\xc0\xbe\x1f\xd3\x1cf\xd9\xf2wc\x1at\x9d\xfe^P\x9fu\xf0\n\xdf<\xd0\x1f\x96\x0f\xd1\x1bC\xa8\xdb\x12\xeb\xf6\xfbL%\xecH_\x1b86O\x03\xdb|\xef\xb6\xf1\xbc\x82\xa7\xc6\xa3\x01}4\x07\xd8\x10\xb8,\x95\xa4r\xb8\x7f)E\'\xec\xcbu\xc6\xa4\xc9\xb0\x84>\x17\x98\x84!:!\xd0YH\x93S\xce\xd7\x86E\xd8\x85\xf3^\xb8cs!:\x1a\xf1f\xce\xd3\x87\x87\xff\x00`\xb1k\xbd'

SENTRY_RUBY_ENCODED = b"eJzVVttu4zYQ/RVCfUgLRNfYsi002z5sf6DoU7cLgyJHEmOKFEjKW6+Rf++QkmM7ziJF0T7UMBzNhZzLOTPKMYI9KLcVPKoioDndLAvIH5YlrykHVpd8sSlhXfNstWTRfdSDtbQFdP4djP4o9sIKrX4xRpuKcBQ5cFIfSIa+TqC3o/2A3kWWl3G2jLPFb3lZLcuqyGePrR0wgahSo5T3kcR0ZFQtsvtoMPoJ2ItlkNQ12vR4mRnrA56Wum3BoIzPbJSDEegcOYyZmJoIRVJCHZFCAdmgiwWzB7NVtPfpg2l1vBfGjVTGPWUduvn6NB8l2Kg6RpQ5LK2nQoYgi6RISvSY1ANluxvlXsCXV8o9POn6RodRfJWvtAaYNvxGbcdh0MZd6k04XSZZ8oBiLVqESvTUK/PZpx6F5CHxB9QUQaP4VEqe5EWSn1XxqKSmPFiy4Mu0YqMxCEwcmn22AMrCekSTVeJRhj+BjY7WEuJO650Nvg/Bt6GGcupPZ8kmaFro4y+GDgMYOye78mqpayoDB7GkkL/I1yqIUxShY8zJaglBuQiFP1mtwi3rUI3UuqFdSG1qjMcuiGWy8CKyLXaHwcOLXcmuVDGnjk7dQqomWREI2gsltr77SIJivjmb9Z5oqFpi9HD7KJ0YqHHxoIPh5Kv0TrfCiJBpifX4Rgz2wE6prlE2E5/yOVUvxnOADHUPQSekvWBBkGMOA/KGOuBbSzEp8XWGODsfirnuw21CtbNt9WLrXC/jbx11Aq5D7nz/cw+Ar8JwzWazr9RTBRG28SXVFlNB+34inufGNI3KmUNsKK6fOai/wuLUsx24CaLyWhefWoDghVtdp03oUL4JDHCdAeob0cBMpaXXfhWq0TPdiujZc9YZBPuIj462dnoarc/4GMwMBj/Qfg3sqRx9Ez4dI0+UtzYfxgheaHu1Aqd1Mq0oXIVsh3EZ+Gsbg3touhYB3CK5HWaFckQICo1oE24VeSR3nXNDlablpqCroixZTetFttqs101RNIyXWVY2Bd1U7zn8nBcr3+Ukr9bZOksnBO7+UH6IFQ9/8eczkhMJfJ3Rd4TRwY0GCFUH8tIfS750gnWk8xOtCB8NMoxMGwHNRDfEdcKSWiKAIQAhOa7l7CIoxqO13Q7Udeft7ZfHqNiEQfQjDrL64Cccl7RCJFe4ENQWg0aVMyOEfeWT3XoHPPCrZ1VySpnrEG5+n2yN1i8vlQbnen4hnCI/37+BCCEcmlMPvtdz8Y/k+PzDXJb/iGaqdNvi2lY/XVgIqaEV6lvtnT4GLBuBBEpdnUUTFRYQhY9a3bkXLEKZBLy/vTpwuumEE3n8QOCm12mne0j9izBNcD5TP7qpn+EYxyRZTPLlnMZhSlMp6jTIaU0t3KA1Z3cB16Y849VQaW8BO1d6ECD538HrOoM3UAuXvMmEf43Pb4B5MUn4fj2D/h7Hw5X+n5Ybsm/eIfvlSP1zjv+/upX+x/35/Oy/fwFCRniE"
