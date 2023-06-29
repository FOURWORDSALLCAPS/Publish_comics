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
    if response.ok:
        server_response = response.json()
        return server_response
    else:
        print('Не удалось получить данные из VK API')


def save_photo_to_group_album(token, api_version, group_id, file_name):
    server_response = get_wall_upload_server(token, api_version, group_id)

    upload_url = server_response.get('response', {}).get('upload_url')

    if not upload_url:
        print(f'Не удалось получить URL загрузки')

    files = {'photo': open(file_name, 'rb')}
    response = requests.post(upload_url, files=files)

    if response.ok:
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

        if response.ok:
            return response.json()
        else:
            print(f'Не удалось сохранить фото в альбом')


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

    if response.ok:
        print(f'Комикс успешно размещен на стене')
    else:
        print(f'Не удалось разместить комикс на стене')


def download_comic(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    if response.ok:
        server_response = response.json()
        image_url = server_response['img']
        image_response = requests.get(image_url)
        if image_response.ok:
            image_file = open(os.path.join('', 'comic.png'), 'wb')
            image_file.write(image_response.content)
            image_file.close()
            return server_response
        else:
            print(f'Не удалось скачать изображение комикса')
    else:
        print(f'Не удалось получить данные комикса по URL')


def main():
    env = Env()
    env.read_env()
    access_token = env('VK_ACCESS_TOKEN')
    api_version = '5.131'
    group_id = env('VK_GROUP_ID')
    file_name = 'comic.png'
    url = f'https://xkcd.com/info.0.json'
    response = requests.get(url)
    if response.ok:
        server_response = response.json()
        pages_number = server_response['num']
        comic_number = random.randint(1, pages_number)
        comment = download_comic(comic_number)['alt']
        image_response = save_photo_to_group_album(access_token, api_version, group_id, file_name)
        post_photo_to_wall(access_token, api_version, group_id, image_response, comment)
        os.remove('comic.png')


if __name__ == '__main__':
    main()
