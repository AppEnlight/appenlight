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
// # AppEnlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/

angular.module('appenlight.services.typeAheadTagHelper', []).factory('typeAheadTagHelper', function () {
    var typeAheadTagHelper = {tags: []};
    typeAheadTagHelper.aheadFilter = function (item, viewValue) {
        //dont show "deeper" autocomplete like level:foo with exception of application ones
        var label_text = item.text || item;
        if (label_text.charAt(label_text.length - 1) != ':' && viewValue.indexOf(':') === -1 && label_text.indexOf('resource:') !== 0) {
            return false;
        }
        if (viewValue.length > 2) {
            // with apps we need to do it differently
            if (viewValue.toLowerCase().indexOf('resource:') == 0) {
                viewValue = viewValue.split(':').pop();
            }
            // check if tags match
            if (label_text.toLowerCase().indexOf(viewValue.toLowerCase()) === -1) {
                return false;
            }
        }
        return true;
    };
    typeAheadTagHelper.removeSearchTag = function (tag) {
        console.log(typeAheadTagHelper.tags);
        var indexValue = _.indexOf(typeAheadTagHelper.tags, tag);
        typeAheadTagHelper.tags.splice(indexValue, 1);

    };
    typeAheadTagHelper.addSearchTag = function (tag) {
        // do not allow dupes - angular will complain
        var found = _.find(typeAheadTagHelper.tags, function (existingTag) {
            return existingTag.type == tag.type && existingTag.value == tag.value
        });
        if (!found) {
            typeAheadTagHelper.tags.push(tag);
        }
    };

    return typeAheadTagHelper;
});
