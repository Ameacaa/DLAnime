from colorama import Fore, init
from bs4 import BeautifulSoup
import requests
import sys
import re
import os


class Page:
    def __init__(self, name : str, episode : str, pagelink : str):
        self.path     :str = str(os.path.join(os.path.join(os.environ['USERPROFILE']), f'Videos\\Animes\\{name}\\'))
        self.name     :str = name
        self.episode  :str = episode
        self.pagelink :str = pagelink
    def info(self):
        print(Fore.BLUE + f"{self.name} (Ep:{self.episode:>4}) - {self.pagelink}")

class Video:
    def __init__(self, links, page : Page):
        self.page  :Page = page
        self.links :list = links
    def info(self):
        self.page.info()
        [print(Fore.CYAN + f'\t- {link}') for link in self.links]

# Second Functions
def GetList(obj):
    if type(obj) is not list:
        return [obj]
    else:
        return obj

def GetSoup(url):
    html = requests.get(url).text
    return BeautifulSoup(html, 'lxml')

def GetTitle(string : str):
    for r in ['Assistir', 'Legendado', '-', 'Animes', 'Online']:
        string = string.replace(r, '')    
    return string.strip()

def GetEpisode(string : str):
    string = string[string.find('Episódio') + len('Episódio'):].split()[0]
    return string.strip()

# Main Functions
def GetPages(urls):
    urls = GetList(urls)
    pages = []
    
    # Step 1 - Get URLS
    for url in urls:
        soup = GetSoup(url)
        # Get URLS
        nextPage = soup.find_all('a', 'next')
        if ( len(nextPage) > 0 ):
            urls.append(nextPage[0].get('href'))
        # Get Pages
        for page in soup.find_all('a', 'col'):
            name = GetTitle(soup.title.text)
            ep = GetEpisode(page.get('title'))
            link = page.get('href')
            pages.append(Page(name=name, episode=ep, pagelink=link))
    return pages

def GetVideo(pages):
    pages = GetList(pages)
    videos = []
    for page in pages:
        html = requests.get(page.pagelink).text
        urls = []
        for string in html.splitlines():
            if string.find('<video') != -1 or string.find('<source') != -1 and string.find('src=') != -1:
                try:
                    urls.append(re.search("(?P<url>https?://[^\s]+)", string).group("url"))
                except:
                    print(Fore.RED + 'Error in insering video object')
        videos.append(Video(GetList(urls), page))
    return videos

def GetVideo(links):
    links = GetList(links)
    videos = []
    for link in links:
        html = requests.get(link).text
        urls = []
        for string in html.splitlines():
            if string.find('<video') != -1 or string.find('<source') != -1 and string.find('src=') != -1:
                try:
                    urlfound = None
                    urlfound = re.search("(?P<url>https?://[^\s]+)", string)
                    if urlfound != None:
                        urls.append(urlfound.group("url")) 
                except:
                    print(Fore.RED + 'Error in insering video object')
        videos.append(Video(GetList(urls), Page('_AnimeDL', str(hash(link)), 'Unkown')))
    return videos

# Download Function
def DownloadFile(video : Video):
    # Check if directory exist
    path = video.page.path
    if not os.path.exists(path):
        os.makedirs(path)
    # Change path for file path
    path = path + video.page.episode + ".mp4"
    # Check if exist a url for this video
    if len(urls) <= 0:
        print('No URL found')
        return
    # Download mp4 link
    url = video.links[0]
    r = requests.get(url)
    f = open( path, 'wb');
    print('Downloading')
    for chunk in r.iter_content(chunk_size=255): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    print ("Done")
    f.close()
    
    
    



def GetUrl():
    arg = sys.argv

    if len(arg) == 1:
        print('Put some urls in next')
        quit()
    else:
        urls = []
        isPage = True
        for c in range(1, len(arg)):
            if ['vid', 'v', 'video'] in arg[c]:
                isPage = False
            else:
                urls.append(arg[c])
        return urls, isPage


if __name__ == '__main__':
    BANNER = """
    ___          _                          ____                      __                __
   /   |  ____  (_)___ ___  ___  _____     / __ \____ _      ______  / /___  ____ _____/ /
  / /| | / __ \/ / __ `__ \/ _ \/ ___/    / / / / __ \ | /| / / __ \/ / __ \/ __ `/ __  / 
 / ___ |/ / / / / / / / / /  __(__  )    / /_/ / /_/ / |/ |/ / / / / / /_/ / /_/ / /_/ /  
/_/  |_/_/ /_/_/_/ /_/ /_/\___/____/____/_____/\____/|__/|__/_/ /_/_/\____/\__,_/\__,_/   
                                  /_____/                                                 
    """
    
    os.system("cls")
    urls, isPage = GetUrl()
    init(autoreset=True)
    print(Fore.MAGENTA + BANNER)
    print(Fore.MAGENTA + 'Can take some minutes depending of internet speed and number of videos of the playlist')
    print('-'*100)

    videos = GetVideo(GetPages(urls)) if isPage else GetVideo(urls)

    [video.info() for video in videos]


    for video in videos:
        DownloadFile(video)


# TODO DOWNLOAD
# Download
# TODO BLOB LINK
# https://stackoverflow.com/questions/48034696/python-how-to-download-a-blob-url-video
