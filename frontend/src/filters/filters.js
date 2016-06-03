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

'use strict';

/* Filters */

angular.module('appenlight.filters').
    filter('interpolate', ['version', function (version) {
        return function (text) {
            return String(text).replace(/\%VERSION\%/mg, version);
        }
    }])
    .filter('isoToRelativeTime', function () {
        return function (input) {
            return moment.utc(input).fromNow();
        }
    })

    .filter('round', function () {
        return function (input, precision) {
            return input.toFixed(precision)
        }
    })

    .filter('numberToThousands', function () {
        return function (input) {
            if (input > 1000000) {
                var i = input / 1000000;
                return i.toFixed(1).toString() + 'M'
            }
            else if (input > 1000) {
                var i = input / 1000;
                return i.toFixed(1).toString() + 'k'
            }
            else {
                return input;
            }
        }
    })
    .filter('getOrdered', function () {
        return function (input, filterOn) {
            var ordered = {};
            for (var key in input) {
                ordered[input[key][filterOn]] = input[key];
            }
            return ordered;
        };
    })
    .filter('objectToOrderedArray', function(){
        return function(items, field, reverse) {
            var filtered = [];
            angular.forEach(items, function(item) {
                filtered.push(item);
            });
            filtered.sort(function (a, b) {
                return (a[field] > b[field] ? 1 : -1);
            });
            if(reverse) filtered.reverse();
            return filtered;
        };
    })
    .filter('apdexValue', function () {
        return function (input) {
            if (input.apdex >= 95) {
                return 'satisfactory';
            } else if (input.apdex >= 80) {
                return 'tolerating';
            } else {
                return 'frustrating';
            }
        };
    })
    .filter('truncate', function(){
        return function (text, length, end) {
            if (isNaN(length))
                length = 10;

            if (end === undefined)
                end = "...";

            if (text.length <= length || text.length - end.length <= length) {
                return text;
            }
            else {
                return String(text).substring(0, length-end.length) + end;
            }

        };
    })

;
