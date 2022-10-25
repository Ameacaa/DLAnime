import re
import requests
from bs4 import BeautifulSoup
from colorama import Fore, init
import os

DOWNLOAD_PATH = str(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Videos') + '\\Animes\\')

class PageVideo:
    def __init__(self, anime_name, episode_number, page_link):
        self.anime_name     = anime_name
        self.episode_number = episode_number
        self.page_link      = page_link

    def __str__(self) -> str:
        return f'Anime: {self.anime_name} | Number: {self.episode_number} | PageLink: {self.page_link}'

class Video:
    def __init__(self, path, name, link):
        self.path = DOWNLOAD_PATH + path + '\\'
        self.name = name
        self.link = link

    def __str__(self) -> str:
        return f'Name: {self.name} | Path: {self.path} | Link: {self.link}'

def DownloadFile(name, path, url):
    name = name + ".mp4"
    r = requests.get(url)
    if not os.path.exists(path):
        os.makedirs(path)
    f = open( path + name, 'wb');
    print('Downloading')
    for chunk in r.iter_content(chunk_size=255): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    print ("Done")
    f.close()



def GetList(obj):
    if type(obj) is not list:
        return [obj]
    else:
        return obj

def GetSoup(url):
    html = requests.get(url).text
    return BeautifulSoup(html, 'lxml')

def GetTitle(string : str):
    string = string.removeprefix('Assistir')
    string = string[0:string.find('-')]
    string = string[0:string.find('Legendado')]
    return string

def GetEpisodeNumber(string : str):
    string = string[string.find('Episódio') + len('Episódio'):].split()[0]
    return string

# Step 1 - Get all pages with episode selections
def GetPagesUrl(url):
    counter = 0
    pages_urls = GetList(url)
    while (True):
        if (counter >= len(pages_urls)):
            break
        soup = GetSoup(pages_urls[counter])
        nextPage = soup.find_all('a', 'next')        
        if ( len(nextPage) > 0 ):
            pages_urls.append(nextPage[0].get('href'))
        counter += 1
    return list(dict.fromkeys(pages_urls)) # Return a list without duplicate urls

# Step 2 - Get all link from episodes page selections (return page video link)
def GetPageVideosUrl(url):
    pages_url = GetList(url)
    videos_url = []
    for page in pages_url:
        soup = GetSoup(page)
        videos = soup.find_all('a', 'col')
        for video in videos:
            videos_url.append(PageVideo(GetTitle(soup.title.text), GetEpisodeNumber(video.get('title')), video.get('href')))
    return videos_url

# Step 3 - Get url of the mp4 video
def GetVideoUrl(url):
    pages_video = GetList(url)
    video_url = []
    for page in pages_video:
        html = requests.get(page.page_link).text
        for string in html.splitlines():
            if string.find('<video') != -1 or string.find('<source') != -1 and string.find('src=') != -1:
                try:
                    url = re.search("(?P<url>https?://[^\s]+)", string).group("url")
                    video_url.append(Video(page.anime_name, page.episode_number, url))
                except:
                    print(Fore.RED + 'Error in insering video object')
    return video_url


init(autoreset=True)
# urls = ['https://goyabu.com/assistir/spy-x-family-parte-2/',
#         'https://goyabu.com/assistir/death-note-legendado/',
#         'https://goyabu.com/assistir/black-clover/']

urls = 'https://goyabu.com/assistir/death-note-legendado/'

# Step 1
print(Fore.MAGENTA + 'Pages founds:')
pages_urls = GetPagesUrl(urls)
for pageurl in pages_urls:
    print(Fore.MAGENTA + '\t-' + pageurl)

# Step 2
print(Fore.BLUE + 'Pages Video found:')
pages_video = GetPageVideosUrl(pages_urls)
for pagevideo in pages_video:
    print(Fore.BLUE + '\t-' + str(pagevideo))

print(Fore.CYAN + 'Searching video link to download:')
videos = GetVideoUrl(pages_video)
for video in videos:
    #print(Fore.BLUE + video)
    DownloadFile(name=video.name, path=video.path , url=video.link)

# TODO BLOB LINK
# https://stackoverflow.com/questions/48034696/python-how-to-download-a-blob-url-video