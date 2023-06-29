import requests
import os
import random

from environs import Env


def get_wall_upload_server(token, api_version, group_id):
    params = {
        'access_token': token,
        'v': api_version,
        'group_id': group_id,
    }
    url = f'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=params)
    response.raise_for_status()
    server_response = response.json()
    return server_response


def save_photo_to_group_album(token, api_version, group_id, file_name):
    server_response = get_wall_upload_server(token, api_version, group_id)

    upload_url = server_response.get('response', {}).get('upload_url')

    with open(file_name, 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        server_response = response.json()

    params = {
        'access_token': token,
        'v': api_version,
        'group_id': group_id,
        'server': server_response['server'],
        'photo': server_response['photo'],
        'hash': server_response['hash']
    }

    url = f'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(url, params=params)

    return response.json()


def post_photo_to_wall(token, api_version, group_id, upload_result, comment):
    params = {
        'access_token': token,
        'v': api_version,
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'attachments': f'photo{upload_result["response"][0]["owner_id"]}_{upload_result["response"][0]["id"]}',
        'message': comment
    }

    url = f'https://api.vk.com/method/wall.post'
    response = requests.post(url, data=params)
    response.raise_for_status()


def download_comic(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    server_response = response.json()
    image_url = server_response['img']
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    with open('comic.png', 'wb') as image_file:
        image_file.write(image_response.content)

    return server_response


def main():
    env = Env()
    env.read_env()
    access_token = env('VK_ACCESS_TOKEN')
    api_version = '5.131'
    group_id = env('VK_GROUP_ID')
    file_name = 'comic.png'
    url = f'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    server_response = response.json()
    pages_number = server_response['num']
    comic_number = random.randint(1, pages_number)
    comment = download_comic(comic_number)['alt']
    image_response = save_photo_to_group_album(access_token, api_version, group_id, file_name)
    post_photo_to_wall(access_token, api_version, group_id, image_response, comment)
    os.remove('comic.png')


if __name__ == '__main__':
    main()
