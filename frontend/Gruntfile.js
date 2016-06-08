var fs = require('fs');
var ini = require('ini');
var config = ini.parse(fs.readFileSync('./locations.ini', 'utf-8'))
module.exports = function (grunt) {

    var grunt_conf_obj = {
        pkg: grunt.file.readJSON('package.json'),

        ngtemplates: {
            app: {
                options: {
                    module: 'appenlight.templates'
                },
                cwd: "src",
                src: '**/*.html',
                dest: 'build/templates.js'
            }
        },

        concat: {
            options: {
                // define a string to put between each file in the concatenated output
                separator: '\n;'
            },
            base: {
                src: [
                    "bower_components/underscore/underscore.js",
                    "bower_components/angular/angular.min.js",
                    "bower_components/angular-cookies/angular-cookies.min.js",
                    "bower_components/angular-route/angular-route.min.js",
                    "bower_components/angular-resource/angular-resource.min.js",
                    "bower_components/angular-animate/angular-animate.min.js",
                    "bower_components/angular-bootstrap/ui-bootstrap-tpls.min.js",
                    "bower_components/angular-ui-router/release/angular-ui-router.min.js",
                    "bower_components/angular-toArrayFilter/toArrayFilter.js",
                    "vendors/crel.js",
                    "bower_components/json-human/src/json.human.js",
                    "bower_components/moment/min/moment.min.js",
                    "bower_components/d3/d3.min.js",
                    "bower_components/c3/c3.min.js",
                    "bower_components/angular-smart-table/dist/smart-table.min.js",
                    "bower_components/ment.io/dist/mentio.min.js",
                    "vendors/simple_moment_utc.js",
                    "vendors/reconnecting-websocket.js",
                ],
                dest: "build/base.js",
                nonull: true
            }
            ,
            dev: {
                src: [
                    "src/utils.js",
                    "src/app.js",
                    "build/templates.js",
                    "src/**/*.js",
                    "!src/**/*_test.js"
                ],
                dest: 'build/app.js',
                nonull: true
            },
            dist: {
                src: [
                    'build/base.js',
                    'build/app.js'
                ],
                dest: "build/release/js/appenlight.js",
                nonull: true
            },
        },
        removelogging: {
            dist: {
                src: "build/app.js"
            }
        },
        copy: {
            css: {
                files: [
                    // includes files within path and its sub-directories
                    {
                        expand: true,
                        cwd: 'build/release/css',
                        src: ['front.css'],
                        dest: config.ae_statics_location + '/css'
                    },
                    {
                        expand: true,
                        cwd: 'build/release/css',
                        src: ['front.css'],
                        dest: config.ae_webassets_location + '/appenlight/css'
                    }
                ]
            },
            js: {
                files: [
                    // includes files within path and its sub-directories
                    {
                        expand: true,
                        cwd: 'build/release/js',
                        src: ['**'],
                        dest: config.ae_statics_location + '/js'
                    },
                    {
                        expand: true,
                        cwd: 'build/release/js',
                        src: ['**'],
                        dest: config.ae_webassets_location + '/appenlight/js'
                    }
                ]
            }
        },
        watch: {
            dev: {
                files: ['<%= concat.dev.src %>', 'src/**/*.html', '!build/*.js'],
                tasks: ['ngtemplates', 'concat:dev', 'concat:dist', 'copy:js']
            },
            css: {
                files: ['css/**/*.less', 'css/**/*.css'],
                tasks: ['less', 'copy:css']
            }
        },

        less: {
            dev: {
                files: {
                    "build/release/css/front.css": "css/front_app.less"
                }
            }
        }

    };

    grunt.initConfig(grunt_conf_obj);

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-bower-concat');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks("grunt-remove-logging");
    grunt.loadNpmTasks('grunt-angular-templates');
    grunt.loadNpmTasks('grunt-contrib-less');


    grunt.registerTask('styles', ['less']);
    grunt.registerTask('test', ['jshint', 'qunit']);

    grunt.registerTask('default', ['ngtemplates', 'concat:base', 'concat:dev', 'removelogging', 'concat:dist', 'less', 'copy:js', 'copy:css']);

};
