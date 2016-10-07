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

angular.module('appenlight.components.adminPartitionsView', [])
    .component('adminPartitionsView', {
        templateUrl: 'components/views/admin-partitions-view/admin-partitions-view.html',
        controller: AdminPartitionsViewController
    });

AdminPartitionsViewController.$inject = ['sectionViewResource'];

function AdminPartitionsViewController(sectionViewResource) {
    var vm = this;
    vm.permanentPartitions = [];
    vm.dailyPartitions = [];
    vm.loading = {partitions: true};
    vm.dailyChecked = false;
    vm.permChecked = false;
    vm.dailyConfirm = '';
    vm.permConfirm = '';


    vm.loadPartitions = function (data) {
        var permanentPartitions = vm.transformPartitionList(
            data.permanent_partitions);
        var dailyPartitions = vm.transformPartitionList(
            data.daily_partitions);
        vm.permanentPartitions = permanentPartitions;
        vm.dailyPartitions = dailyPartitions;
        vm.loading = {partitions: false};
    };

    vm.setCheckedList = function (scope) {
        var toTest = null;
        if (scope === 'dailyPartitions'){
            toTest = 'dailyChecked';
        }
        else{
            toTest = 'permChecked';
        }

        if (vm[toTest]) {
            var val = true;
        }
        else {
            var val = false;
        }
        console.log('scope', scope);
        _.each(vm[scope], function (item) {
            _.each(item[1].pg, function (index) {
                index.checked = val;
            });
            _.each(item[1].elasticsearch, function (index) {
                index.checked = val;
            });
        });
    }


    vm.transformPartitionList = function (inputList) {
        var outputList = [];

        _.each(inputList, function (item) {
            var time = [item[0], {
                elasticsearch: [],
                pg: []
            }]
            _.each(item[1].pg, function (index) {
                time[1].pg.push({name: index, checked: false})
            });
            _.each(item[1].elasticsearch, function (index) {
                time[1].elasticsearch.push({
                    name: index,
                    checked: false
                })
            });
            outputList.push(time);
        });
        return outputList;
    };

    sectionViewResource.get({section:'admin_section', view: 'partitions'},
        vm.loadPartitions);

    vm.partitionsDelete = function (partitionType) {
        var es_indices = [];
        var pg_indices = [];
        _.each(vm[partitionType], function (item) {
            _.each(item[1].pg, function (index) {
                if (index.checked) {
                    pg_indices.push(index.name)
                }
            });
            _.each(item[1].elasticsearch, function (index) {
                if (index.checked) {
                    es_indices.push(index.name)
                }
            });
        });
        console.log(es_indices, pg_indices);

        vm.loading = {partitions: true};
        sectionViewResource.save({section:'admin_section',
            view: 'partitions_remove'}, {
            es_indices: es_indices,
            pg_indices: pg_indices,
            confirm: 'CONFIRM'
        }, vm.loadPartitions);

    }

}
