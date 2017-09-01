// Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

if (!String.prototype.trim) {
    String.prototype.trim = function () {
        return this.replace(/^\s+|\s+$/g, '');
    };

    String.prototype.ltrim = function () {
        return this.replace(/^\s+/, '');
    };

    String.prototype.rtrim = function () {
        return this.replace(/\s+$/, '');
    };

    String.prototype.fulltrim = function () {
        return this.replace(/(?:(?:^|\n)\s+|\s+(?:$|\n))/g, '').replace(/\s+/g, ' ');
    };
}

function decodeEncodedJSON (input){
    try{
        var val = JSON.parse(input);
        delete doc;
        return val;
    }catch(exc){
        console.error('decodeEncodedJSON:' + exc + ' input:' + input);
        delete doc;
    }
}

function parseTagsToSearch(searchParams) {
    var params = {};
    _.each(searchParams.tags, function (t) {
        if (!_.has(params, t.type)) {
            params[t.type] = [];
        }
        params[t.type].push(t.value);
    });
    if (searchParams.page > 1){
     params.page = searchParams.page;
    }
    return params;
}

function parseSearchToTags(search) {
    var config = {page: 1, tags: [], type:''};
    _.each(_.pairs(search), function (obj) {
        if (_.isArray(obj[1])) {
            _.each(obj[1], function (obj2) {
                config.tags.push({type: obj[0], value: obj2});
            })
        } else {
            if (obj[0] == 'page') {
                config.page = obj[1];
            }
            else if (obj[0] == 'type') {
                config.type = obj[1];
            }
            else {
                config.tags.push({type: obj[0], value: obj[1]});
            }

        }
    });
    return config;
}


/* returns ISO date string from UTC now - timespan */
function timeSpanToStartDate(timeSpan){
    var amount = Number(timeSpan.slice(0,-1));
    var unit = timeSpan.slice(-1);
    return moment.utc().subtract(amount, unit).format();
}

/* Sets server validation messages on form using angular machinery +
* custom key holding actual error messages */
function setServerValidation(form, errors){
    console.log('form', form);
    if (typeof form.ae_validation === 'undefined'){
        form.ae_validation = {};
        console.log('create ae_validation key');
    }
    for (var key in form.ae_validation){
        form.ae_validation[key] = [];
        console.log('clear key:', key);
    }
    console.log('errors:',errors);

    for (var key in form){
        if (key[0] !== '$' && key !== 'ae_validation'){
            form[key].$setValidity('ae_validation', true);
        }
    }
    if (typeof errors !== undefined){
        for (var key in errors){
            if (typeof form[key] !== 'undefined'){
                form[key].$setValidity('ae_validation', false);
            }
            // handle wtforms and colander errors based on
            // whether we have list of erors or a single error in a key
            if (angular.isArray(errors[key])){
                form.ae_validation[key] = errors[key];
            }
            else{
                form.ae_validation[key] = [errors[key]];
            }
        }
    }
    return form;
}
