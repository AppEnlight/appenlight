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
            $rootScope.$apply(function (scope) {
                _.each(data, function (message) {
                    console.log('channelstream-message', message);
                    if(typeof message.message.topic !== 'undefined'){
                        $rootScope.$emit(
                            'channelstream-message.'+message.message.topic, message);
                    }
                    else{
                        $rootScope.$emit('channelstream-message', message);
                    }
                });
            });
        };
        stateHolder.websocket.onclose = function (event) {
            console.log('closed');
        };

        stateHolder.websocket.onerror = function (event) {
            console.log('error');
        };
    }.bind(this));
}
