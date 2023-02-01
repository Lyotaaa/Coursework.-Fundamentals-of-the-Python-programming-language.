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
        
print(*open_a_token('token.ini'), sep='\n')