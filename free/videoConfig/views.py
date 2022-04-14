from django.views.generic import TemplateView, View
from rest_framework import serializers
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect

from free.models import Apparatus
import requests


janus_server_address = settings.JANUS_SERVER_ADDRESSS
janus_stream_admin_key = settings.JANUS_STREAM_ADMIN_KEY






def connect_janus_stream(server_address):

    data = {
        "janus": "create",
        "transaction": "transaction-x",
    }
    response = requests.post(f'{server_address}/', json = data)

    json_ret = response.json()

    if(response.status_code != 200 or  json_ret['janus']!='success'):
        print("Error in connection with JANUS")
        print(response.json())
        return (0, 0)

    #get session_id
    session_id = json_ret['data']['id']

    #connect to streamming plugin
    data = {
        "janus" : "attach",
        "plugin" : "janus.plugin.streaming",
        "transaction": "transaction-x",
    }

    response = requests.post(f'{server_address}/'+str(session_id), json = data)
    json_ret = response.json()
    if(response.status_code != 200 or  json_ret['janus']!='success'):
        print("Error in connection with JANUS Streamming plugin")
        print(response.json())
        return (0, 0)

    plugin_id = json_ret['data']['id']
    return   (plugin_id, session_id)

def list_streams(server_address):
    plugin_id, session_id = connect_janus_stream(server_address)

    if session_id ==0 or plugin_id == 0:
        return -1

    data = {
        "janus": "message",
        "body": {
            "request": "list"
        },
        "transaction": "transaction-x"
    }

    response = requests.post(f'{server_address}/{session_id}/{plugin_id}', json = data)
    json_ret = response.json()
    try:
        return json_ret['plugindata']['data']['list']
    except:
        print("Error retrieving JANUS Streams")
        return []
    


def stream_info(server_address, stream_id):
    plugin_id, session_id = connect_janus_stream(server_address)
    ret_list = []

    if session_id ==0 or plugin_id == 0:
        return []

    data = {
        "janus": "message",
        "body": {
            "request": "info",
            "id": int(stream_id)
        },
        "transaction": "transaction-x",
    }
    response = requests.post(f'{server_address}/{session_id}/{plugin_id}', json = data)
    json_ret = response.json()
    try: 
        return json_ret['plugindata']['data']['info']
    except:
        print(f"Error retrieving JANUS Stream {stream_id} info")
        return {}




def create_stream(server_address, stream_admin_key, name, description):
    plugin_id, session_id = connect_janus_stream(server_address)

    if session_id ==0 or plugin_id == 0:
        return {}

    data = {
        "janus": "message",
        "body": {
            
                "request" : "create",
                "type" : "rtp",
                "name" : name,
                "description" : description,
                "audio" : False,
                "video" : True,
                #"data" : <true|false, whether the mountpoint will have datachannels; false by default>,
                "permanent" : True,
                "videoport" : 0,  #Porto onde são recebidos os pacotes do stream (ver comando de gstreamer) 
                "videopt" : 126,  #nao alterar #96
                "videortpmap" : "H264/90000",  #nao alterar 
                "videofmtp" : "profile-level-id=42e01f;packetization-mode=1", #nao alterar 
                "admin_key": stream_admin_key
        },
        "transaction": "transaction-x",
    }

    response = requests.post(f'{server_address}/{session_id}/{plugin_id}', json = data)
    json_ret = response.json()
    if(json_ret['janus']!= 'success'):
        print(f"Error creating JANUS Stream "+json_ret)
        return {}
    json_plugin = json_ret['plugindata']['data']
    try: 
        return json_plugin['stream'] 
    except:
        print(f"Error creating JANUS Stream "+json_plugin)
        return {}
 

def destroy_stream(server_address, stream_admin_key, stream_id):
    plugin_id, session_id = connect_janus_stream(server_address)

    if session_id ==0 or plugin_id == 0:
        return {}

    data = {
        "janus": "message",
        "body": {

                "request" : "destroy",
                "id": int(stream_id),
                "permanent" : True,
                "admin_key": stream_admin_key
            
        },
        "transaction": "transaction-x",
    }

    response = requests.post(f'{server_address}/{session_id}/{plugin_id}', json = data)
    json_ret = response.json()
    if(json_ret['janus']!= 'success'):
        print(f"Error destroying JANUS Streams {stream_id}")
        return {}
    json_plugin = json_ret['plugindata']['data']
    if(json_plugin['streaming'] != 'destroyed'):
        print(f"Error destroying JANUS Streams {stream_id}")
        return {}
    else:
        return json_ret['plugindata']['data']
 


class ApparatusSerializer(serializers.ModelSerializer):
    apparatus_type = serializers.SlugRelatedField(
        many=False, 
        read_only=True,
        slug_field="name"
    )
    class Meta:
        model = Apparatus
        fields = ['id',  'video_config','location', 'apparatus_type']



class VideoConfigList(PermissionRequiredMixin, TemplateView):
    template_name='videoConfig_list.html'
    permission_required = 'user.is_supersuser'
    def get_context_data(self, **kwargs):          
        context = super().get_context_data(**kwargs)                     
        context["aparatus_list"] = []
        
        for a in set(Apparatus.objects.all()):
            context["aparatus_list"].append(ApparatusSerializer(a).data)
        context['janus_info'] = list_streams(janus_server_address)
        print(context['janus_info'])
        return context


class VideoConfig(PermissionRequiredMixin,TemplateView):
    template_name='videoConfig.html'
    permission_required = 'user.is_supersuser'
    def get_context_data(self, **kwargs):          
        context = super().get_context_data(**kwargs)                     
        apparatus_id = self.kwargs['id']
        ap = Apparatus.objects.filter(id = apparatus_id).first()
        context["ap"] = ApparatusSerializer(ap).data
        try:
            si = stream_info(janus_server_address, ap.video_config['stream_id'])
            context['stream_info'] = si
            context['stream_address'] = janus_server_address.split('/')[2].split(':')[0]
            context['stream_port'] = si['media'][0]['port']
        except:
            context['stream_info'] = {}
        return context

class VideoConfigAssignStream(PermissionRequiredMixin,View):
    permission_required = 'user.is_supersuser'
    def get(self, request, *args, **kwargs):    
        apparatus_id = kwargs['id']
        print(apparatus_id)
        ap = Apparatus.objects.filter(id = apparatus_id).first()
        si = {}
        try:
            si = stream_info(janus_server_address,  ap.video_config['stream_id'])
        except:
            pass
            new_stream = create_stream(janus_server_address, 
                            janus_stream_admin_key, 
                            f'ap_{ap.id}_{ap.apparatus_type}',
                            f'{ap.apparatus_type} {ap.id} in {ap.location}', 
                )
        
            if(new_stream != {}):
                ap.video_config = {'stream_id': new_stream['id'], 'stream_server': janus_server_address}
                ap.save()
        return redirect('video-config', id = apparatus_id)

class VideoConfigRemoveStream(PermissionRequiredMixin,View):
    permission_required = 'user.is_supersuser'
    def get(self, request, *args, **kwargs):            
        apparatus_id = kwargs['id']
        ap = Apparatus.objects.filter(id = apparatus_id).first()
        si = {}
        try:
            si = stream_info(janus_server_address, ap.video_config['stream_id'])
        except:
            pass
        destroyed_stream = destroy_stream(janus_server_address, 
                        janus_stream_admin_key, 
                        ap.video_config['stream_id'],
            )
        ap.video_config = {} 
        ap.save()
        return redirect('video-config', id = apparatus_id)

