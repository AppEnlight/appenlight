module.exports = function(config){
  config.set({

    basePath : './',

    files : [
      'node_modules/angular/angular.js',
      'node_modules/angular-route/angular-route.js',
      'node_modules/angular-mocks/angular-mocks.js',
      'node_modules/angular-scenario/angular-scenario.js',
      'src/**/*.js'
    ],

    autoWatch : true,

    frameworks: ['jasmine'],

    browsers : ['Chrome'],

    plugins : [
      'karma-chrome-launcher',
      'karma-firefox-launcher',
      'karma-jasmine',
      'karma-junit-reporter'
    ],

    junitReporter : {
      outputFile: 'test_out/unit.xml',
      suite: 'unit'
    }

  });
};
