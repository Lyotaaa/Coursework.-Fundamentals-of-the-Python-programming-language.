import os
import requests
import datetime
import json
from tqdm import tqdm
from pprint import pprint

def open_a_token(file_name):
    with open(os.path.join(os.getcwd(), file_name)) as f:
        res = json.load(f)
        vk_token = res['VK']['token']
        vk_id = res['VK']['page_id']
        ya_token = res['Yandex']['token']
    return [vk_token, vk_id, ya_token]        
      
def find_max_resolution(glossary):
    max_resolution = 0
    for i in range(len(glossary)):
        result = glossary[i].get('width') * glossary[i].get('height')
        if result > max_resolution:
            max_resolution = result
            max_photo = i
    return glossary[max_photo].get('url'), glossary[max_photo].get('type')

def time_convert(unix):
    time_unix = datetime.datetime.fromtimestamp(unix)
    normal_time = time_unix.strftime('time: %H:%M:%S date: %d.%m.%Y')
    return normal_time

class vkontakte:
    def __init__(self, token, version='5.131'):
        self.token = token[0]
        self.id = token[1]
        self.version = version
        self.initial_params = {'access_token': self.token, 'v': self.version}
        self.json, self.download_information = self.photo_data_collection()
        
    def get_information_about_the_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id,
                  'album_id': 'profile',
                  'photo_sizes': 1,
                  'extended': 1}
        response = requests.get(url, params={**self.initial_params, **params}).json()
        return response['response']['count'], response['response']['items']

    def photo_data_collection(self):
        data_collection = {}
        json_file = []
        number_photos, photo_elements = self.get_information_about_the_photo()
        for i in range(number_photos):
            photo_address, photo_size = find_max_resolution(photo_elements[i]['sizes'])
            
            if _ not in json_file['file_name']:
                json_file.append({
                "file_name": f'{photo_elements[i]["likes"]["count"]}.jpeg',
                "size": photo_size
                })
        # if name not in json_file[file_name]:
        #     data_collection[int(i) + 1] = {
        #         "file_name": f'{photo_elements[i]["likes"]["count"]}.jpeg',
        #         "url": photo_address
        #         }
        # data_collection[photo_elements[i]['likes']['count']] = {'url':photo_address}
        #     photo_address = find_max_resolution(photo_elements[i]['sizes'])
        #     likes = photo_elements[i]['likes']['count']
        #     photo_date = time_convert(photo_elements[i]['date'])
        #     new_value = data_collection.get(likes)
        #     new_value.append({'add_name': photo_date,
        #                       'url_picture': photo_address})
        #                       #'size': picture_size})
        #     data_collection[likes] = new_value
        return json_file, data_collection
    
if __name__ == '__main__':
    res = vkontakte(open_a_token('token.ini'))
    pprint(res.json)