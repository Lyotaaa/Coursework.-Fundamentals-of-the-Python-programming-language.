import os
import sys
import requests
import datetime
import json
import time
from tqdm import tqdm
from pprint import pprint
from configparser import ConfigParser

def open_a_token(file_name):
    cofing = ConfigParser()
    cofing.read(file_name)
    vk_token = cofing['token_info']['VK_token']
    vk_id = cofing['token_info']['page_id']
    ya_token = cofing['token_info']['Yandex_token']
    return [vk_token, vk_id, ya_token]
          
def time_convert(unix):
    time_unix = datetime.datetime.fromtimestamp(unix)
    normal_time = time_unix.strftime('time-%H.%M.%S date-%d.%m.%Y')
    return normal_time

class Vkontakte:
    
    def __init__(self, token, count, version='5.131'): 
        self.token = token[0]
        self.id = token[1]
        self.count = int(count)
        self.url = 'https://api.vk.com/method/photos.get'
        self.version = version
        self.initial_params = {'access_token': self.token, 'v': self.version}
        self.json, self.export_dict = self.photo_data_collection()

    def get_information_about_the_photo(self):
        params = {
            'owner_id': self.id,
            'album_id': 'profile',
            'photo_sizes': 1,
            'extended': 1,
            'count': self.count
        }
        response = requests.get(url=self.url, params={**self.initial_params, **params})
        return response.json()['response']['count'], response.json()['response']['items']

    def find_max_resolution(self, photo_information):
        max_resolution = 0
        for i in range(len(photo_information)):
            result = photo_information[i].get('width') * photo_information[i].get('height')
            if result > max_resolution:
                max_resolution = result
                max_photo = i
        return photo_information[max_photo].get('url'), photo_information[max_photo].get('type')
    
    def photo_data_collection(self):
        data_collection = {}
        json_file = []
        number_photos, photo_elements = self.get_information_about_the_photo()
        if self.count <= number_photos:
            for i in range(self.count):
                photo_address, photo_size = self.find_max_resolution(photo_elements[i]['sizes'])
                file_name = f'{photo_elements[i]["likes"]["count"]}.jpeg'
                date = f'{time_convert(photo_elements[i]["date"])}'
                if file_name not in data_collection:
                    data_collection[file_name] = photo_address
                    json_file.append({"file_name": file_name, "size": photo_size})
                elif file_name in data_collection:
                    data_collection[f'{photo_elements[i]["likes"]["count"]}_{date}.jpeg'] = photo_address
                    json_file.append(({"file_name": f'{photo_elements[i]["likes"]["count"]}_{date}.jpeg',
                                    "size": photo_size}))
            return json_file, data_collection
        else:
            print(f'Ведённое кол-во фотографий нет. Всего фотографий в профиле {number_photos}. Повторите запрос.')
            sys.exit()
        

class YandexDisk:
    
    def __init__(self, folder_name, token):
        self.token = token[2]
        self.url_upload = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        self.url_resources = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {'Authorization': self.token}
        self.folder = self.create_a_folder(folder_name)
                    
    def create_a_folder(self, folder_name):
        params = {'path': folder_name}
        if requests.get(url=self.url_resources, headers=self.headers, params=params).status_code != 200:
            requests.put(url=self.url_resources, headers=self.headers, params=params)
            print(f'Папка "{folder_name}" создана.')
        else:
            print(f'Папка "{folder_name}" уже существует.')
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
        print(f'Количество файлов для загрузки: {len(data_collection)}.')
        for key in tqdm(data_collection.keys()):
            time.sleep(0.5)
            if counter < len(data_collection):
                if key not in files_in_folder:
                    params = {
                        'path': f'{self.folder}/{key}',
                        'url': data_collection[key],
                        'overwrite': 'false'
                    }
                    requests.post(self.url_upload, headers=self.headers, params=params)
                    print(f'\nФайл {key} успешно загружен.')
                    counter += 1
                else:
                    print(f'\nФайл {key} уже существует.')
            else:
                break   
        print(f'Загрузка завершена. Файлов загружено: {counter}.')

if __name__ == '__main__':
    
    res_VK = Vkontakte(open_a_token('confing.ini'), input('Введите кол-во фотографий, которые хотите загрузить: '))
    # pprint(res_VK.json)
    res_YA = YandexDisk('!Test', open_a_token('confing.ini'))
    res_YA.send_to_disk(res_VK.export_dict)
    with open('List of downloadable files.json', 'w') as outfile:
        json.dump(res_VK.json, outfile)
    