import os
import requests
import time
import json
from tqdm import tqdm
from pprint import pprint

def open_a_token(file_name):
    with open(os.path.join(os.getcwd(), file_name)) as f:
        res = json.load(f)
        vk_token = res['VK']['token']
        vk_id = res['VK']['id']
        ya_token = res['Yandex']['token']
    return [vk_token, vk_id, ya_token]        
      
def find_max_resolution(glossary):
    max_resolution = 0
    for i in range(len(glossary)):
        result = glossary[i].get('width') * glossary[i].get('height')
        if max_resolution > result:
            result = max_resolution
            max_photo = i
        return glossary[max_photo].get('url'), glossary[max_photo].get('type')

class vkontakte:
    def __init__(self, token, version='5.131'):
        self.token = token[0]
        self.id = token[1]
        self.version = version
        self.initial_params = {'token': self.token, 'v': self.version}
        self.json, self.export_dict = self._sort_info()

    def _get_photo_info(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id,
                  'album_id': 'profile',
                  'photo_sizes': 1,
                  'extended': 1}
        photo_info = requests.get(url, params={**self.initial_params, **params}).json()['response']
        return photo_info['count'], photo_info['items']

