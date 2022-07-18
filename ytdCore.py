import os
import shutil
from blinker import receiver_connected
from pytube import YouTube
from pytube import Playlist
import tkinter as tk
import pandas as pd
from moviepy.editor import VideoFileClip


#a function taht using pandas loads the ytd_config.csv file data into the variables
def load_config_file(filename='ytd_config.csv'):
    #get location of this python file
    path = os.getcwd()
    print(path)
    #get current directory
    cwd = os.getcwd()
    print(cwd)
    #join cwd and filename to get the full path
    file = cwd + '\\' + filename
    print(file)
    #load the config file
    config_file = pd.read_csv(file)
    #create a dictionary from the config file using the column names as the keys and the first row as the values
    config_dict = config_file.to_dict('records')[0]
    #print the dictionary
    print('Config loaded: ' + str(config_dict))
    #return the config dictionary
    return config_dict
   
#a function that writes the config file from a dictionary 
def save_config_file(config_dict, filename='ytd_config.csv'):
    #create a dataframe from the dictionary
    config_df = pd.DataFrame(config_dict, index=[0])
    #write the dataframe to the config file
    config_df.to_csv(filename, index=False)
    #print a notification that the file has been created
    print('Config saved.')
    #print the path to the file
    print('Path: ' + os.getcwd() + '/' + filename)
    #return the config dictionary
    #return config_dict   

#check if the save dir exists and if not, create it
#and return it's absolute path
def check_save_dir(config_data):
    if not os.path.exists(config_data['save_dir']):
        os.makedirs(config_data['save_dir'])
        print('Save directory created.')
    else:
        print('Save directory already exists.')
    return config_data['save_dir']


#set the default save directory to the current working directory absolute path
def set_default_save_dir(config_data):
    config_data['save_dir'] = os.getcwd()
    #print a notification that the default save directory has been set
    print('Default save directory set.')
    #return the config dictionary
    return config_data


#a function that takes a video stream,
#checks if the stream is valid and if it is,
#returns download video
def download_video(stream):
    #if the stream is valid
    if stream is not None and stream != '':
        #print a notification that the video is downloading
        print('Stream is valid, downloading video...')
        downloaded_video = stream.download()
        #print a notification that the video has been downloaded
        print('Video downloaded.')
        #print video title
        print('Title: ' + stream.title)
        #print video absolute path
        print('Path: ' + downloaded_video)
        #return the video
        return downloaded_video
    #otherwise the stream is invalid and return empty string
    else:
        print('Invalid video stream.')
        return ''

#a function that receives the config dictionary and requests the link data from YouTube
#then returns the dictionary of streams and thumbnails
def get_streams_from_link(config_data):
    #a list of downloaded videos
    selected_streams = []
    thumbnail_urls = []
    #if the link contains a 'list' it's a playlist
    #if it doesn't but contains a 'v=' or 'watch' it's a video
    print('analyzing link: ' + config_data['link'])
    if 'list' in config_data['link']:
        print('Link is a playlist.')
        #create a playlist object from the link
        playlist = Playlist(config_data['link'])
        #print number of videos in the playlist
        print('Detected ' + str(len(playlist.videos)) + ' videos in the playlist.')
        #for each video in the playlist, request the video streams and select the best stream then downlad it
        for video in playlist.videos:
            #request the video streams
            video_streams = video.streams
            thumbnail = video.thumbnail_url
            #select the best stream
            best_stream = video_streams.filter(progressive=True).order_by('resolution').desc().first()
            #add stream to a list of selected streams
            selected_streams.append(best_stream)
            thumbnail_urls.append(thumbnail)
            #download the video   
    elif 'watch' in config_data['link'] or 'v=' in config_data['link']:
        print('Link is a video.')
        #if the link contains a 'v='or 'watch' it's a video
        #create a video object from the link
        video = YouTube(config_data['link'])
        thumbnail = video.thumbnail_url
        #get the video streams
        video_streams = video.streams.filter(progressive=True)
        #order the streams by the quality
        video_streams = video_streams.order_by('resolution').desc()
        #get the first stream in the list
        selected_stream = video_streams.first() 
        #save selected stream for download
        selected_streams.append(selected_stream)
        thumbnail_urls.append(thumbnail)
    #otherwise the link is invalid and return empty streams
    else:
        print('Link is invalid. Nothing has been downloaded')
        selected_streams = None
    #returns a list of videos either from playlist or single video from the link
    #it is in a video list format
    print('Selected streams for download: '+ str(len(selected_streams)) + ' streams.')
    #create a dictionary with key streams and value the list of selected streams and key thumbnail and value the thumbnail url
    streams_thumbs = {'streams': selected_streams, 'thumbnails': thumbnail_urls}
    print('Streams and thumbnail urls: '+str(streams_thumbs))
    return streams_thumbs

global download_count
download_count = 0
#a function that receives a list of streams and downloads them
def download_streams(streams_thumbs, no_input=True):
    streams = streams_thumbs['streams']
    thumbs = streams_thumbs['thumbnails']
    print(thumbs)
    download_count = 0
    downloaded_videos = []
    #check that streams is not empty and not none
    if streams is not None and streams != '':
        #print the title of all the videos in the stream list
        total_size = 0.0
        for i in range(len(streams)):
            print('Title: ' + streams[i].title)
            print('Size: ' + str(streams[i].filesize))
            print('Thumbnail: ' + thumbs[i])
            total_size += streams[i].filesize
        #convert total size to MB
        total_size = total_size / 1000000
        #take player input to confirm download
        print('Total size: ' + str(total_size*1.6) + 'MB.')
        #store the decision to download
        decision = False
        if not no_input:
            print('Confirm download of selected videos:')
            confirm_download = input('Enter "y" to download or "n" to cancel: ')
        #if the user confirms the download
            if confirm_download == 'y':
                decision = True
            elif confirm_download == 'n':
                decision = False
        else:
            decision = True
        #if the decision is true, download the videos
        if decision:
            #for each stream in the list
            for stream in streams:
                #download the video
                downloaded_videos.append(download_video(stream))
                download_count += 1
                print('Downloaded ' + str(download_count) + ' videos.')
        #print a notification that the videos have been downloaded
        print('Videos downloaded.')
    #otherwise display a notification that the videos were not downloaded
    else:
        print('No videos streams received, nothing to download.')
    #return the list of downloaded videos
    return downloaded_videos

    
#a function that takes an mp4 file and using videofileclip converts it to mp3
#with an option to remove the original file
def mp4tomp3(video_file):
    #print a notification that the video is converting
    print('Converting video to mp3...')
    #create a video file clip object from the video file
    video_clip = VideoFileClip(video_file)
    #create a mp3 file name from the video file name
    mp3_file = video_file.replace('.mp4', '.mp3')
    #convert the video file clip to mp3
    video_clip.audio.write_audiofile(mp3_file)
    video_clip.close()
    #print a notification that the video has been converted
    print('Video converted.')
    #return the mp3 file name
    return mp3_file

#a function that takes a list of downloaded mp4 files and converts them to mp3
def convert_downloaded(downloaded_videos, remove_source=True):
    print('Converting downloaded videos to mp3...')
    #a list of mp3 files
    converted_videos = []
    #for each mp4 file in the list
    for video_file in downloaded_videos:
        #convert the mp4 file to mp3
        converted_videos.append(mp4tomp3(video_file))
    if remove_source:
        print('Removing source videos...')
        #go through the file list again and remove all the files
        for video_file in downloaded_videos:
            #remove the mp4 file
            os.remove(video_file)
    #return the list of mp3 files
    return converted_videos


#a function that moves the mp3 files to a specified directory
def organize_files(files_list, config_data):
    #print a notification that the files are being organized
    print('Organizing files...')
    organized_files = []
    #check save_dir
    check_save_dir(config_data)
    #for each file in the list
    for file in files_list:
        #extract the file name from the file path
        file_name = file.split('\\')[-1]
        print('Orginizing file: ' + file_name)
        #check if the file exists in the current directory
        if os.path.exists(file_name):
            #check if file already exists in the sav_dir of the config data
            if os.path.exists(config_data['save_dir'] + '\\' + file_name):
                #print file already exists notification
                print('File already exists in the designated save directory.')
                #delete the file
                print('Deleting temporary file...')
                os.remove(file_name)
                organized_files.append(config_data['save_dir'] +'\\'+ file_name)
            #otherwise inform the user that the file is being moved
            else:
                print('Moving file...')
                #move the file to the save_dir
                shutil.move(file, config_data['save_dir'])
                #add the file to the list of organized files
                organized_files.append(config_data['save_dir'] +'\\'+ file_name)
                #print a notification that the file has been moved
                print('File moved.')
        else:
            #print a notification that the file does not exist
            print('Error: File not found.')
        
    #print a notification that the files have been organized
    print('Files organized.')
    for file in organized_files:
        print(file.split('\\')[-1])
    #return the list of mp3 files
    return organized_files


#a debugging function that asks user for inputs to override the config file
#and updates the config dictionary
def override_config(config_data):
    #for each key in the config dictionary
    #ask the user for the value of the key
    for key in config_data:
            print('Current value for ' + key + ': ' + config_data[key])
            print('To override ' + key + ' input a new value and press enter, or leavy empty to skip: ')
            key_override = input()
            if key_override != '':
                config_data[key] = key_override
    return config_data


#a function that checks if the format is saved to mp3 and if so, converts the downloaded mp4 files to mp3
def convert_if_mp3(downloaded_videos, config_data):
    #check if the format is mp3
    if config_data['format'] == 'mp3':
        #convert the mp4 files to mp3
        processed_videos = convert_downloaded(downloaded_videos, remove_source=True)
        #return the list of mp3 files
        return processed_videos
    elif config_data['format'] == 'mp4':
        processed_videos = downloaded_videos
    #return the list of desired files
    return processed_videos



#main logic function pipeline
def run_downloader(config_data, default_save_dir=False):
    if default_save_dir:
        config_data['save_dir'] = set_default_save_dir(config_data)
    #makes sure the save directory exists and if not creates it
    save_dir = check_save_dir(config_data)
    #gets the link from the config data and returns a list of best streams to download
    selected_streams = get_streams_from_link(config_data)
    #downloads the streams and returns the downloaded files
    downloaded_videos = download_streams(selected_streams, True)
    #if the format in the config data is mp3, convert the mp4 files to mp3
    processed_files = convert_if_mp3(downloaded_videos, config_data)
    #organize the files and move them to the save_dir
    organized_files = organize_files(processed_files, config_data)



        


########DATA CONFIG OVERRIDE FUNCTIONS########
#function that sets the folder to mp3 or mp4 dpending on the config data
def set_default_save_dir(config_data):
    #if the format is mp3
    if config_data['format'] == 'mp3':
        #set the save_dir to the mp3 folder
        save_dir = config_data['save_dir'] + '\\mp3'
    #if the format is mp4
    elif config_data['format'] == 'mp4':
        #set the save_dir to the mp4 folder
        save_dir = config_data['save_dir'] + '\\mp4'
    #else set the save_dir to other
    else:
        save_dir = config_data['save_dir'] + '\\other'
    #return the save_dir
    config_data['save_dir'] = save_dir
    print('Save directory set to: ' + save_dir)
    save_config_file(config_data)
    return save_dir

#function that sets save dir to a specific folder in the current directory
def set_save_dir(config_data, save_dir):
    #set the save_dir to current directory + folder_name
    config_data['save_dir'] = save_dir
    print('Save directory set to: ' + str(save_dir))
    save_config_file(config_data)
    return save_dir

#function that overrides the format in the config data
def set_format(config_data, format='mp3'):
    #set the format in the config data
    config_data['format'] = format
    #return the config data
    print('Format set to ' + format)
    save_config_file(config_data)
    return format

#function that overrides the link in the config data
def set_link(config_data, link=''):
    #set the link in the config data
    config_data['link'] = link
    #return the config data
    print('Link set to ' + config_data['link'])
    save_config_file(config_data)
    return link



########DEBUGGING########
#------CONFIG FILE--------
#load the config file
#config_data = load_config_file()

#----OVERRIDE ALL--------
##manual override all config data
#config_data = override_config(config_data)

#------OVERRIDE FORMAT-------
#override the format in the config data
#set_format(config_data, 'mp4')

#------OVERRIDE SAVE DIR------   
#override the save_dir to default mp3 or mp4 folder names depending on the download format
#choose_save_dir(config_data)

#------OVERRIDE LINK------
###exapmle links
#4 video test playlist, linkt to the 2nd video
#link1 = 'https://www.youtube.com/watch?v=j8RvP1nMMXo&list=PL26iWboCbd3SLogMP1d-zqO03XpEjJ6Nc&index=2'
#a single video link
#link2 = 'https://www.youtube.com/watch?v=VJlBtnPsCeA'
#a direct link to a 2 video playlist
#link3 = 'https://www.youtube.com/playlist?list=PL26iWboCbd3Tj02lnmn53p_mZUhabWYlY'
#list of links
#links = [link1, link2, link3]

#override the link in the config data
#set_link(config_data, link3)

#------RUN DOWNLOADER------
#run the downloader
#run_downloader(config_data)

##########################

#to do:
#make the code retreive miniature from the stream together with other data such as title and filesize
#make sure to consider for temporary files when estimating the space needed for the download