from googleapiclient.discovery import build
import isodate
import csv


# Получаем список плейлистов
def get_playlists_list(channel, youtube):
    playlists_list = []
    next_page_token = None
    while True:
        if next_page_token is None:
            request = youtube.playlists().list(
                part='snippet',
                channelId=channel,
                maxResults=50
            )
        else:
            request = youtube.playlists().list(
                part='snippet',
                channelId=channel,
                pageToken=next_page_token,
                maxResults=50
            )
        response = request.execute()
        for playlist in response['items']:
            playlists_list += [[playlist['id'], playlist['snippet']['title']]]
        if response.get('nextPageToken') is None:
            break
        else:
            next_page_token = response['nextPageToken']
    return playlists_list


# Получаем список видео
def get_videos_list(playlists_list, youtube):
    videos_list = []
    for playlist in playlists_list:
        next_page_token = None
        while True:
            if next_page_token is None:
                request = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist[0],
                    maxResults=50
                )
            else:
                request = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist[0],
                    pageToken=next_page_token,
                    maxResults=50
                )
            response = request.execute()
            for video in response['items']:
                videos_list += [[video['snippet']['resourceId']['videoId'], playlist[1], video['snippet']['title']]]
            if response.get('nextPageToken') is None:
                break
            else:
                next_page_token = response['nextPageToken']
        print('Обработан плейлист ' + '"' + playlist[1] + '"')
    print('Всего найдено видео: ' + str(len(videos_list)))
    return videos_list


# Получаем искомую информацию по каждому видео
def get_videos_info(videos_list, youtube):
    for video in videos_list:
        request = youtube.videos().list(
            part='statistics, snippet, contentDetails',
            id=video[0]
        )
        response = request.execute()

        # Обрабатываем исключения, возникающие при обработке приватных видео, видео с закрытыми лайками и прочего такого
        if response['items']:
            if response['items'][0]['snippet'].get('publishedAt') is not None:
                video += [response['items'][0]['snippet']['publishedAt']]
            else:
                video += ['']
            if response['items'][0]['statistics'].get('viewCount') is not None:
                video += [response['items'][0]['statistics']['viewCount']]
            else:
                video += ['']
            if response['items'][0]['statistics'].get('likeCount') is not None:
                video += [response['items'][0]['statistics']['likeCount']]
            else:
                video += ['']
            if response['items'][0]['statistics'].get('dislikeCount') is not None:
                video += [response['items'][0]['statistics']['dislikeCount']]
            else:
                video += ['']
            if response['items'][0]['statistics'].get('favoriteCount') is not None:
                video += [response['items'][0]['statistics']['favoriteCount']]
            else:
                video += ['']
            if response['items'][0]['statistics'].get('commentCount') is not None:
                video += [response['items'][0]['statistics']['commentCount']]
            else:
                video += ['']
            if response['items'][0]['contentDetails'].get('duration') is not None:
                video += [int(isodate.parse_duration(response['items'][0]['contentDetails']['duration']).total_seconds())]
            else:
                video += ['']
        else:
            video += ['', '', '', '', '', '', '']

    print('Всего видео обработано: ' + str(len(videos_list)))
    return videos_list


# Записываем полученные данные в файл data.csv
def write_videos_info(videos_list, channel):
    with open('data_of_' + channel + '.csv', 'w', encoding='utf8', newline='') as dataFile:
        writer = csv.writer(dataFile, delimiter=';')
        writer.writerow(['video_id', 'playlist_name', 'video_name', 'publication_date', 'views', 'likes', 'dislikes',
                         'favorites', 'comments', 'duration_seconds'])
        writer.writerows(videos_list)


# Сслыка на исследуемый канал: https://www.youtube.com/user/Alex007SC2
# ID исследуемого канала: 'UC3ptU7hyNeFlJdvQj2nZHJg'
if __name__ == '__main__':
    api_key = input('Введите Ваш ключ YouTube API: ')
    channel = input('Введите ID искомого канала: ')
    youtube_build = build('youtube', 'v3', developerKey=api_key)

    write_videos_info(
        get_videos_info(
            get_videos_list(
                get_playlists_list(channel, youtube_build),
                youtube_build),
            youtube_build), channel)
