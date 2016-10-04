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

angular.module('appenlight.components.channelstream', [])
    .component('channelstream', {
        controller: ChannelstreamController,
        bindings: {
            config: '='
        }
    });

ChannelstreamController.$inject = ['$rootScope', 'stateHolder', 'userSelfPropertyResource'];

function ChannelstreamController($rootScope, stateHolder, userSelfPropertyResource){
    if (stateHolder.AeUser.id === null){
        return
    }
    userSelfPropertyResource.get({key: 'websocket'}, function (data) {
        stateHolder.websocket = new ReconnectingWebSocket(this.config.ws_url + '/ws?conn_id=' + data.conn_id);
        stateHolder.websocket.onopen = function (event) {
            console.log('open');
        };
        stateHolder.websocket.onmessage = function (event) {
            var data = JSON.parse(event.data);
            _.each(data, function (message) {
                console.log('channelstream-message', message);
                if(typeof message.message.topic !== 'undefined'){
                    $rootScope.$broadcast(
                        'channelstream-message.'+message.message.topic, message);
                }
                else{
                    $rootScope.$broadcast('channelstream-message', message);
                }
            });
        };
        stateHolder.websocket.onclose = function (event) {
            console.log('closed');
        };

        stateHolder.websocket.onerror = function (event) {
            console.log('error');
        };
    });
}
