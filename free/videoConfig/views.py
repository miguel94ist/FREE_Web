from django.views.generic import TemplateView, View
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect

from free.models import Apparatus
import requests
import random

janus_server_address = settings.JANUS_SERVER_ADDRESS
janus_stream_admin_key = settings.JANUS_STREAM_ADMIN_KEY

def connect_janus_stream(server_address):

    data = {
        "janus": "create",
        "transaction": "transaction-x",
    }
    try:
        response = requests.post(f'{server_address}/', json = data, verify=False)
    except:
        return None

    if response.status_code != 200 :
        print("Error in connection with JANUS")
        return None

    json_ret = response.json()
    if json_ret['janus']!='success':
        print("Error in connection with JANUS")
        return None

    #get session_id
    session_id = json_ret['data']['id']

    #connect to streamming plugin
    data = {
        "janus" : "attach",
        "plugin" : "janus.plugin.streaming",
        "transaction": "transaction-x",
    }

    response = requests.post(f'{server_address}/'+str(session_id), json = data, verify=False)
    json_ret = response.json()

    if(response.status_code != 200 or  json_ret['janus']!='success'):
        print("Error in connection with JANUS Streamming plugin")
        return None

    try:
        plugin_id = json_ret['data']['id']
        return   (plugin_id, session_id)
    except:
        return None

def list_streams(server_address, connection):
    try:
        plugin_id, session_id = connection
    except:
        return None

    data = {
        "janus": "message",
        "body": {
            "request": "list"
        },
        "transaction": "transaction-x",
    }

    response = requests.post(f'{server_address}/{session_id}/{plugin_id}', json = data, verify=False)
    json_ret = response.json()
   
    try:
        return json_ret['plugindata']['data']['list']
    except:
        print("Error retrieving JANUS Streams")
        return None

def stream_info(server_address, stream_id):
    try:
        plugin_id, session_id = connect_janus_stream(server_address)
    except:
        return None
    ret_list = []


    data = {
        "janus": "message",
        "body": {
            "request": "info",
            "id": int(stream_id)
        },
        "transaction": "transaction-x",
    }
    try:
        response = requests.post(f'{server_address}/{session_id}/{plugin_id}', json = data, verify=False)
        json_ret = response.json()
    except:
        return None

    try: 
        return json_ret['plugindata']['data']['info']
    except:
        print(f"Error retrieving JANUS Stream {stream_id} info")
        return {}




def create_stream(server_address, stream_admin_key, name, description,stream_secret):
    try:
        plugin_id, session_id = connect_janus_stream(server_address)
    except:
        return None

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
                "videopt" : 96,  #nao alterar #96
                "videortpmap" : "H264/90000",  #nao alterar 
                "videofmtp" : "profile-level-id=42e01f;packetization-mode=1", #nao alterar 
                "admin_key": stream_admin_key
        },
        "transaction": "transaction-x",
    }
 
    response = requests.post(f'{server_address}/{session_id}/{plugin_id}', json = data, verify=False)
    json_ret = response.json()
    
    if(json_ret['janus']!= 'success'):
        print(f"Error creating JANUS Stream ")
        return None
    json_plugin = json_ret['plugindata']['data']
    try: 
        return json_plugin['stream'] 
    except:
        print(f"Error creating JANUS Stream ")
        return None
 

def destroy_stream(server_address, stream_admin_key, stream_id, stream_secret):
    try:
        plugin_id, session_id = connect_janus_stream(server_address)
    except:
        return None

    data = {
        "janus": "message",
        "body": {
                "request" : "destroy",
                "id": int(stream_id),
                "permanent" : True,
                "admin_key": stream_admin_key,
                "secret": stream_secret
        },
        "transaction": "transaction-x",
    }

    response = requests.post(f'{server_address}/{session_id}/{plugin_id}', json = data, verify=False)
    json_ret = response.json()

    if(json_ret['janus']!= 'success'):
        print(f"Error destroying JANUS Streams {stream_id}")
        return None

    json_plugin = json_ret['plugindata']['data']
    if(json_plugin['streaming'] != 'destroyed'):
        print(f"Error destroying JANUS Streams {stream_id}")
        return None
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
            try:
                video_strema_id = int(a.video_config)
                a.video_config = {'stream_id': video_strema_id, 
                                'stream_server': janus_server_address,
                                }
                a.save()
            except:
                pass
            context["aparatus_list"].append(ApparatusSerializer(a).data)
        connection = connect_janus_stream(janus_server_address)

        if connection == None:
            context['janus_error'] = 'Connect'
        else:
            context['janus_info'] = list_streams(janus_server_address, connection)
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
            stream_id = ap.video_config['stream_id']
        except:
            context['stream_info'] = {}
            return context
        si = stream_info(janus_server_address, stream_id)
        if si == None:
            context['janus_error'] = 'Connect'
            context['stream_info'] = {}
            return context
        try:
            context['stream_info'] = si
            context['video_config'] = ap.video_config
            context['stream_config']={
                'video_server': janus_server_address.split('/')[2].split(':')[0],
                'video_port' : si['media'][0]['port'],
                #'video_port' : si['videoport'],
                'apparatus_location': ap.location,
                'apparatus_name': ap.apparatus_type.slug,
                'apparatus_id' :  ap.id,
            }
        except:
            context['janus_warning'] = 'Video stream information mismatch between FREE and JANUS'
        return context

class ErrorVideoConfig(VideoConfig):
    def get_context_data(self, **kwargs):          
        context = super().get_context_data(**kwargs)                     
        context["janus_error"] = True
        return context


class VideoConfigAssignStream(PermissionRequiredMixin,View):
    permission_required = 'user.is_supersuser'
    def get(self, request, *args, **kwargs):    
        apparatus_id = kwargs['id']
        ap = Apparatus.objects.filter(id = apparatus_id).first()
        try:
            s_id = ap.video_config['stream_id']
            si = stream_info(janus_server_address,  s_id)
        except:
            si = {}
        if si == None:
            return redirect('video-config-error', id = apparatus_id)
        if si != {}:
            return redirect('video-config', id = apparatus_id)

        stream_secret = str(random.randint(1, 99999999))
        new_stream = create_stream(janus_server_address, 
                        janus_stream_admin_key, 
                        f'ap_{ap.id}_{ap.apparatus_type.slug}',
                        f'{ap.apparatus_type} {ap.id} in {ap.location}', 
                        stream_secret
            )
        if(new_stream == None):
            return redirect('video-config-error', id = apparatus_id)
            
        if(new_stream != {} ):
            ap.video_config = {'stream_id': new_stream['id'], 
                                'stream_server': janus_server_address,
                                'secret':stream_secret}
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
            return redirect('video-config-error', id = apparatus_id)

        destroyed_stream = destroy_stream(janus_server_address, 
                        janus_stream_admin_key, 
                        ap.video_config['stream_id'],
                        ap.video_config['secret'],
            )
        try:
            if destroyed_stream['streaming'] == 'destroyed':
                ap.video_config = {} 
                ap.save()
                return redirect('video-config', id = apparatus_id)
        except:
            pass
        return redirect('video-config-error', id = apparatus_id)

