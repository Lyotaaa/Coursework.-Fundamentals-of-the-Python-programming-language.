import os
import requests
import datetime
import json
import time
from tqdm import tqdm
from pprint import pprint

def open_a_token(file_name):
    with open(os.path.join(os.getcwd(), file_name)) as f:
        res = json.load(f)
        vk_token = res['VK']['token']
        vk_id = res['VK']['page_id']
        ya_token = res['Yandex']['token']
    return [vk_token, vk_id, ya_token]        
      
def time_convert(unix):
    time_unix = datetime.datetime.fromtimestamp(unix)
    normal_time = time_unix.strftime('time-%H.%M.%S date-%d.%m.%Y')
    return normal_time

class Vkontakte:

    def __init__(self, token, version='5.131'):
        self.token = token[0]
        self.id = token[1]
        self.url = 'https://api.vk.com/method/photos.get'
        self.version = version
        self.initial_params = {'access_token': self.token, 'v': self.version}
        self.json, self.export_dict = self.photo_data_collection()

    def get_information_about_the_photo(self):
        params = {'owner_id': self.id,
                  'album_id': 'profile',
                  'photo_sizes': 1,
                  'extended': 1
                  }
        response = requests.get(url=self.url, params={**self.initial_params, **params})
        return response.json()['response']['count'], response.json()['response']['items']

    def find_max_resolution(self, glossary):
        max_resolution = 0
        for i in range(len(glossary)):
            result = glossary[i].get('width') * glossary[i].get('height')
            if result > max_resolution:
                max_resolution = result
                max_photo = i
        return glossary[max_photo].get('url'), glossary[max_photo].get('type')
    
    def photo_data_collection(self):
        data_collection = {}
        json_file = []
        number_photos, photo_elements = self.get_information_about_the_photo()
        for i in range(number_photos):
            photo_address, photo_size = self.find_max_resolution(photo_elements[i]['sizes'])
            file_name = f'{photo_elements[i]["likes"]["count"]}_{time_convert(photo_elements[i]["date"])}.jpeg'
            json_file.append({"file_name": file_name, "size": photo_size})
            data_collection[file_name] = photo_address
        return data_collection, data_collection
    
class YandexDisk:

    def __init__(self, folder_name, token, num=5):
        self.token = token[2]
        self.number_of_photos = num
        self.url_upload = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        self.url_resources = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {'Authorization': self.token}
        self.folder = self.create_a_folder(folder_name)
                    
    def create_a_folder(self, folder_name):
        params = {'path': folder_name}
        if requests.get(url=self.url_resources, headers=self.headers, params=params).status_code != 200:
            requests.put(url=self.url_resources, headers=self.headers, params=params)
            print(f'Папка "{folder_name}" создана.\n')
        else:
            print(f'Папка "{folder_name}" уже создана.\n')
        return folder_name

    def get_information_about_folder(self, folder_name):
        params = {'path': folder_name}
        response = requests.get(url=self.url_resources, headers=self.headers, params=params)
        response = response.json()['_embedded']['items']
        name_files = []
        for i in response:
            name_files.append(i['name'])
        return name_files
    
    def send_to_disk(self, data_collection):
        counter = 0
        files_in_folder = self.get_information_about_folder(self.folder)
        for key, i in zip(data_collection.keys(), tqdm(range(self.number_of_photos))):
            time.sleep(1)
            if counter < self.number_of_photos:
                if key not in files_in_folder:
                    params = {
                        'path': f'{self.folder}/{key}',
                        'url': data_collection[key],
                        'overwrite': 'false'
                    }
                    requests.post(self.url_upload, headers=self.headers, params=params)
                    print(f'\nФайл {key} успешно добавлен')
                    counter += 1
                else:
                    print(f'Файл {key} уже соществует')
            else:
                break   
        


if __name__ == '__main__':
    res_VK = Vkontakte(open_a_token('token.ini'))
    res_YA = YandexDisk('Проверка', open_a_token('token.ini'), 10)
    res_YA.send_to_disk(res_VK.export_dict)

    # res = YandexDisk('_Проверка', open_a_token('token.ini'))
    # pprint(res.json)
    # res = Vkontakte(open_a_token('token.ini'))
    # pprint(res_VK.json)

        
# for i in tqdm(range(10)):
#     time.sleep(2)