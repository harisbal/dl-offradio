
# coding: utf-8

# In[25]:


import os
import requests
import re
import youtube_dl
import tqdm
from bs4 import BeautifulSoup
from time import gmtime, strftime


# In[26]:


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'downloaded':
        song = d['filename']
        print('Downloading {}'.format(song))
        


# In[27]:


def fetch_offradio_playlist(url='http://www.offradio.gr/player'):
    r  = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'html5lib')
    
    data = []
    artists = []
    tracks = []

    class_name = re.compile('view view-playlist view-id-playlist view-display-id-block_1 view-dom-id-*')
    divTag = soup.find('div', class_=class_name)
    glinks = divTag.find_all('a', class_='lgoogle')

    for gl in glinks:
        s = gl['href']
        s = s.split('as_q=',1)[1]

        artist, track = s.split('+-+', 1)
        artist = artist.replace('+', ' ')
        track = track.replace('+', ' ')

        artists.append(artist)
        tracks.append(track)
        
    playlist = [' - '.join(x) for x in (zip(artists, tracks))]
    
    return playlist 


# In[51]:


def dl_ytPlaylist(playlist):
    
    fldr_time = strftime("%Y-%m-%d %H%M%S", gmtime())
    fldr_dl = 'dl_playlists/{}/%(title)s.%(ext)s'.format(fldr_time)
    

    # Load tqdm with size counter instead of file counter
    with tqdm.tqdm(total=len(playlist), desc='Downloading') as pbar:
        for song in playlist:
            pbar.set_postfix(song=song, refresh=False)
            pbar.update()

            ydl_opts = {
                'outtmpl': fldr_dl ,
                'default_search': 'ytsearch1:{}'.format(song),
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
            }
                        
            with youtube_dl.YoutubeDL(ydl_opts) as ytdl:
                ytdl.download('-1') # I don't like the '-1', it justs requires a invalid query


def main():
    
    # Fetch the list
    print('Fetch playlist')
    playlist = fetch_offradio_playlist()
    
    # Download it
    dl_ytPlaylist(playlist)


if __name__ == '__main__':
    main()
