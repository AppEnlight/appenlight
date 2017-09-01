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
