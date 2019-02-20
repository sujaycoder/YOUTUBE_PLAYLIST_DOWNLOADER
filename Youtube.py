import pytube
from googleapiclient import discovery
from pytube import exceptions
import os
import time
a = time.time()
# declare switch case
url_list = []

# declare api key
api_key = str(input('Enter the Youtube api key: '))

folder = str(input('Enter Folder Name: '))

path = os.path.join('{}\\{}' .format(os.getcwd(), folder))
                    
try:
    os.mkdir(path)
except os.error:
    print('Something went wrong Please restart the program')
    exit(0)


def switch(form):
    return {
        1: '1080p',
        2: '720p',
        3: '480p',
        4: '360p',
        5: True
        }.get(form, 'invalid')


def goto():
    print("1. 1080p 2. 720p 3. 480p 4. 360p 5. mp3")
    choice_format = int(input('Enter Your Choice: '))
    return choice_format
   

def file_format(resolution, url_yt):
    if resolution is not True:
        if resolution == '720p' or resolution == '1080p' or resolution == '480p':
            yt = pytube.YouTube(url_yt)
            video = yt.streams.filter(resolution=resolution, mime_type='video/webm').all()
            audio = yt.streams.filter(only_audio=True, abr='160kbps').all()
            print('%s is Downloading Size = %.2f MB' % (yt.title, (video[0].filesize/(1024*1024)) +
                                                     (audio[0].filesize/(1024*1024))))
            name = yt.title
            name = name.split()
            name = name[0] + '.webm'
            video[0].download(filename='video')
            audio[0].download(filename='audio')
            cmd = 'ffmpeg -i video.webm -i audio.webm -c copy {}' .format(name)
            os.system(cmd)
            os.remove('audio.webm')
            os.remove('video.webm')
            move = 'move {} {}' .format(name, folder)
            os.system(move)

        else:
            yt = pytube.YouTube(url_yt)
            video = yt.streams.filter(resolution=resolution, mime_type='video/mp4').all()
            print('%s is Downloading Size = %.2f MB' % (yt.title, video[0].filesize/(1024*1024)))
            name = yt.title
            name = name.split()
            video[0].download(filename='%s' % name[0])
            name = name[0] + '.mp4'
            move = 'move {} {}' .format(name, folder)
            os.system(move)
    else:
        yt = pytube.YouTube(url_yt)
        audio = yt.streams.filter(only_audio=resolution, abr='160kbps').all()
        print('%s is Downloading Size = %.2f MB' % (yt.title, audio[0].filesize/(1024*1024)))
        audio[0].download(filename='audio')
        name = yt.title
        name = name.split()
        name = name[0] + '.mp3'
        os.system('ffmpeg -i audio.webm -vn -ab 160k -ar 44100 -y {}' .format(name))
        os.remove('audio.webm')
        os.system('move {} {}' .format(name, folder))


def choice_yt(link_yt):
    choice_format = goto()
    category = switch(choice_format)
    if category == 'invalid':
        choice_format = goto()
        category = switch(choice_format)
    if 'list' in link_yt:
        print('Enter S for all file or I for individual files: ')
        cho = str(input())
        if cho == 's' or cho == 'S':
            print(category)
            return category, 999
        else:
            video_list = []
            while True:
                opt = int(input('Enter Video number: '))
                video_list.append(opt-1)
                cont = str(input('Want to add more Videos(Y/N): '))
                if cont == 'n' or cont == 'N':
                    break

            return category, video_list
    else:
        return category


def list_youtube(link_yt, **kwargs):
    # build the google api client
    client = discovery.build('youtube', 'v3', developerKey=api_key)
    # if the link refers a playlist
    res = None
    if 'list' in link_yt:
        try:
            obj = client.playlistItems().list(**kwargs)
            res = obj.execute()
        except pytube.exceptions.PytubeError:
            print("----------------------Enter Valid link:--------------------")
        # Show all the Details of videos
        for i in range(len(res['items'])):
            video_id = res['items'][i]['contentDetails']['videoId']
            url_list.append('https://www.youtube.com/watch?v=%s&id=%s' % (video_id, res['items'][i]['id']))
            print('%d. Video Title: %s' % (len(url_list), res['items'][i]['snippet']['title']))
        # if found next page Token it will call back until it is not the last page
        if 'nextPageToken' in res:
            token = res['nextPageToken']
            list_youtube(link_yt, part='snippet, contentDetails', pageToken=token, playlistId=lid)
            # chose how many videos
        cho, yt_list = choice_yt(link_yt)
        if yt_list == 999:
            for i in range(len(url_list)):
                file_format(cho, url_list[i])
        else:
            for i in range(len(yt_list)):
                file_format(cho, url_list[yt_list[i]])
        print('Successfully Download All')
        b = time.time()
        print((b-a)/360)
        exit(0)

    else:
        try:
            obj = client.videos().list(**kwargs)
            res = obj.execute()
        except pytube.exceptions.PytubeError:
            print("----------------------Enter Valid link:--------------------")
            start()
        id_yt = res['items'][0]['id']
        print('Video Title: %s' % res['items'][0]['snippet']['title'])
        url_list.append('https://www.youtube.com/watch?v=%s&id=%s' % (kwargs['id'], id_yt))
        cho = choice_yt(link_yt)
        file_format(cho, url_list[len(url_list)-1])
        print('Successfully Download All')

        b = time.time()
        print((b-a)/60)
        exit(0)


def start():
    li = str(input('Enter Link Here: '))
    return li


link = start()


if 'list' in link:
    link_code = '\0'
    url = link.replace('list=', '$')
    for k in range(len(url)):
        if url[k] == '$':
            link_code = url[k+1]
            for j in range(k+2, len(url)):
                if url[j] == '&':
                    break
                link_code = link_code + url[j]
    lid = link_code
    list_youtube(link, part='snippet, contentDetails', playlistId=lid)
else:
    url = link.split('&')
    url = url[0].split('v=')
    vid = url[1]
    list_youtube(link, part='snippet, contentDetails', id=vid)
