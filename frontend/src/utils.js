// # Copyright (C) 2010-2016  RhodeCode GmbH
// #
// # This program is free software: you can redistribute it and/or modify
// # it under the terms of the GNU Affero General Public License, version 3
// # (only), as published by the Free Software Foundation.
// #
// # This program is distributed in the hope that it will be useful,
// # but WITHOUT ANY WARRANTY; without even the implied warranty of
// # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// # GNU General Public License for more details.
// #
// # You should have received a copy of the GNU Affero General Public License
// # along with this program.  If not, see <http://www.gnu.org/licenses/>.
// #
// # This program is dual-licensed. If you wish to learn more about the
// # App Enlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/

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
