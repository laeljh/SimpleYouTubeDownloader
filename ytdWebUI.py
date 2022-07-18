#import downloader core
from calendar import c
from cgitb import text
import time
from typing_extensions import Self
from pkg_resources import yield_lines
from regex import R
import ytdCore as ytd
import streamlit as st
import streamlit.components.v1 as components



import tkinter as tk
from tkinter import filedialog

# Set up tkinter
root = tk.Tk()
root.withdraw()

# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

#style adjustments for the download list
def hide_header(df):
    style = df.style.hide_index()
    style.hide_columns()
    st.write(style.to_html(), unsafe_allow_html=True)

def folder_picker(default_dir, config_data):
    # Folder picker button    
    fp_button = st.button('Browse...')
    if fp_button:
        folder_path = filedialog.askdirectory(master=root)
    else:
        folder_path = default_dir
    ytd.set_save_dir(config_data, folder_path)
    return folder_path


def download_progress(target_number):
    current_file_count = len(ytd.os.listdir(ytd.os.getcwd()))
    if(target_number+current_file_count > current_file_count):
        return current_file_count/target_number

#this script uses streamlit to create a web UI for the youtube downloader
#create static header elelements
def build_header():
    #title
    st.title("YouTube Downloader")
    #subtitle
    st.subheader("Download videos or playlists from YouTube, save them as mp3 or mp4")
    #text
    st.text("This is a simple web UI for the youtube downloader. "+"\n"+
            "You can download videos or playlists from YouTube and save them as mp3 or mp4."+"\n"+
            "No ads no premium, safe files only.")

#create dynamic part
def build_dynamic(config_data, link = '', format = '', save_dir = ''):
    #extract link, format and save_dir from config_data if was not explicitly provided
    if link=='':
        link = config_data['link']
    if format=='':
        format = config_data['format']
    if save_dir=='':
        save_dir = config_data['save_dir']
    print('Loaded data from config_data to GUI variables')
    print(link, format, save_dir)
    
    
    #LINK URL INPUT
    #text
    st.text("Enter the URL of the video or playlist you want to download:")
    #text input
    input_url = st.text_input("URL:", link)
    if input_url != link:
        link = input_url
        ytd.set_link(config_data, link)
        
        
    #FORMAT SELECTION
    #create dropdown menu with options mp3 and mp4
    st.text("Select the format you want to save the video as:")
    #assign index to the chosen format 1 for mp4 and 0 for mp3 
    if format == 'mp4':
        sel_index = 1
    else:
        sel_index = 0
    format_choice = st.selectbox("Format:", ["mp3", "mp4"],sel_index)
    print('Selected format: '+format_choice)
    if format_choice != format:
        format = format_choice
        ytd.set_format(config_data, format)
    
    #SAVE DIRECTORY
    #create a save dir path input and file browser button
    st.text("Select or input the path to save the video:")
    #file browser button
    input_dir = st.text_input('Selected path:', folder_picker(save_dir, config_data))
    #input_dir = folder_picker(save_dir, config_data)
    if input_dir != save_dir:
        print('Input dir differs from save dir: '+input_dir+ ' vs ' +save_dir)
        print('Updating...')
        save_dir = input_dir
        ytd.set_save_dir(config_data, input_dir)
        
        
    #ANALYZE BUTTON
    #create a download button
    #when clicked on download button start download
    info_box = st.info("Depending on the list size, the querry with YouTube can take up to several minutes...")
    analyze_button = st.button("Analyze and download")


    if analyze_button:
        ytd.save_config_file(config_data)
        config_data = ytd.load_config_file()
        print("Analyzing.")
        #get the streams and thumbnails
        streams_thumbs = get_streams_from_link(config_data)
        print('Building download list...')
        #download_list = build_download_entry(streams_thumbs)
        download_list = create_display_download_list(streams_thumbs)
        #preview_table = st.table(download_list) 
        #once the download starts as the videos are downloaded, mark them on the download list
        #and show the progress
        #check how many files there are in the current working directory
        
        #then as the files change update the counters
        #and show the progress
        
        placeholder = st.empty()         
        downloaded_files = download_videos(streams_thumbs)
        processed_files = fix_file_format(downloaded_files, config_data)
        organized_files = move_and_clean(processed_files, config_data)
        placeholder.header('Done!')
        loading_animation = st.balloons()
        save_information = st.text('Saved '+str(len(organized_files))+' files to '+config_data['save_dir'])

def download_videos(streams_thumbs):
    #variables for the downloader
    downloaded_files = []
    #extract the streams
    streams = streams_thumbs['streams']
    #count the streams 
    stream_count = len(streams)
    #create a placeholder for the download progress
    status = st.empty()
    substatus = st.empty()
    progress = st.empty()
    status.header('Downloading...')
    progress.progress(0)
    substatus.text('This can take a few minutes...')
    progres_mod = float(1.0/stream_count)
    for i in range(stream_count):
        progress.progress(float(i)*progres_mod)
        substatus.text('Downloading '+str(i+1)+' of '+str(stream_count))
        downloaded_file = ytd.download_video(streams[i])
        downloaded_files.append(downloaded_file)
    progress.progress(1.0)
    progress.empty()
    substatus.empty()
    status.empty()
    return downloaded_files

def fix_file_format(downloaded_files, config_data):
    #check if the format is mp3
    if config_data['format'] == 'mp3':
        #convert the mp4 files to mp3
        processed_files = convert_files_to_mp3(downloaded_files, remove_source=True)
        #return the list of mp3 files
        return processed_files
    elif config_data['format'] == 'mp4':
        processed_files = downloaded_files
    #return the list of desired files
    return processed_files

def move_and_clean(processed_files, config_data):
    status = st.empty()
    substatus = st.empty()
    progress = st.empty()
    #print a notification that the files are being organized
    print('Organizing files...')
    status.header('Organizing...')
    substatus.text('This shouldn\'t take long...')
    progress.progress(0.0)
    organized_files = []
    number_of_files = len(processed_files)
    progress_mod = float(1.0/number_of_files)
    print('Progress mod: '+str(progress_mod))
    #check save_dir
    ytd.check_save_dir(config_data)
    #for each file in the list
    for i in range(number_of_files):
        file = processed_files[i]
        #extract the file name from the file path
        file_name = file.split('\\')[-1]
        substatus.text('Working on: '+file_name)
        progress.progress(float(i)*progress_mod)
        print('Orginizing file: ' + file_name)
        #check if the file exists in the current directory
        if ytd.os.path.exists(file_name):
            #check if file already exists in the sav_dir of the config data
            if ytd.os.path.exists(config_data['save_dir'] + '\\' + file_name):
                #print file already exists notification
                print('File already exists in the designated save directory.')
                #delete the file
                print('Deleting temporary file...')
                ytd.os.remove(file_name)
                organized_files.append(config_data['save_dir'] +'\\'+ file_name)
            #otherwise inform the user that the file is being moved
            else:
                print('Moving file...')
                #move the file to the save_dir
                ytd.shutil.move(file, config_data['save_dir'])
                #add the file to the list of organized files
                organized_files.append(config_data['save_dir'] +'\\'+ file_name)
                #print a notification that the file has been moved
                print('File moved.')
        else:
            #print a notification that the file does not exist
            print('Error: File not found.')
        progress.progress(1.0)
        status.empty()
        substatus.empty()
        progress.empty()
    #print a notification that the files have been organized
    print('Files organized.')
    for file in organized_files:
        print(file.split('\\')[-1])
    #return the list of mp3 files
    return organized_files


def convert_files_to_mp3(downloaded_files, remove_source=True):
    print('Converting downloaded videos to mp3...')
    status = st.empty()
    substatus = st.empty()
    progress = st.empty()
    progress.progress(0.0)
    status.header('Processing...')
    substatus.text('This can take a few minutes...')
    num_of_files = len(downloaded_files)
    #a list of mp3 files
    converted_videos = []
    #for each mp4 file in the list
    progress_mod = float(1.0/num_of_files)
    print('Progress mod: '+str(progress_mod))
    for i in range(num_of_files):
        video_file = downloaded_files[i]
        progress.progress(float(i)*progress_mod)
        substatus.text('Converting '+str(i+1)+' of '+str(num_of_files))
        #convert the mp4 file to mp3
        converted_videos.append(ytd.mp4tomp3(video_file))
    if remove_source:
        print('Removing source videos...')
        substatus.text('Removing source videos...')
        #go through the file list again and remove all the files
        for video_file in downloaded_files:
            #remove the mp4 file
            ytd.os.remove(video_file)
    progress.progress(1.0)
    #return the list of mp3 files
    status.empty()
    substatus.empty()
    progress.empty()
    return converted_videos

        
#takes a dictionary of streams and thumbnails, separates them, them creates a download list and UI data  
def create_display_download_list(streams_thumbs):
    status = st.empty()
    substatus = st.empty()
    substatus2 = st.empty()
    progress = st.empty()
    
    status.header("Analyzing...")
    substatus.text("Retrieving stream information...")
    progress.progress(0.0)
    #create a download list header
    total_filesize_mb = 0
    print('Building download list...')
    streams = streams_thumbs['streams']
    download_info_list = []
    progress_mod = float(1.0/len(streams))
    for i in range(len(streams)):      
        progress.progress(float(i)*progress_mod) 
        #create a numbered list of the streams:
        stream_title = streams[i].title
        substatus.text('Analyzing '+str(i+1)+' of '+str(len(streams)))
        print('Creating a list entry for '+stream_title)
        stream_size = streams[i].filesize
        #convert stream size from bytes to MB
        stream_size_mb = round(stream_size/1000000, 2)
        entry = [i+1, stream_title, stream_size_mb]
        download_info_list.append(entry) 
        total_filesize_mb += stream_size_mb
        total_filesize_mb = round(total_filesize_mb, 2)                     
    print('Done building download list')
    progress.progress(1.0)
    #convert total filesize from bytes to MB
    substatus.text('Estimate total download size: '+str(total_filesize_mb)+' MB')
    substatus2.text('Estimate total required temp sizes: '+str(total_filesize_mb*1.6)+' MB')
    print('download_info_list: '+str(download_info_list))
    preview_string = ""
    for entry in download_info_list:
        nl_symbol = '\n'
        entry_string = str(entry[0])+'. '+entry[1]+' ('+str(entry[2])+' MB)'+nl_symbol
        preview_string += entry_string
    with st.expander("View the songs list:"):
     st.write(preview_string)    

    status.empty()
    substatus2.empty()
    substatus.empty()
    progress.empty()
    return download_info_list

#a function that receives the config dictionary and requests the link data from YouTube
#then returns the dictionary of streams and thumbnails
def get_streams_from_link(config_data):
    #a list of downloaded videos
    selected_streams = []
    thumbnail_urls = []
    #placeholder for ui data
    ui_status = st.header('Retreiving stream information...')
    ui_data = st.empty()
    ui_data.text('Working...')
    #if the link contains a 'list' it's a playlist
    #if it doesn't but contains a 'v=' or 'watch' it's a video
    print('analyzing link: ' + config_data['link'])
    if 'list' in config_data['link']:
        print('Link is a playlist.')
        #create a playlist object from the link
        playlist = ytd.Playlist(config_data['link'])
        playlist_len = len(playlist.videos)
        stream_errors = []
        ui_error = st.empty()
        #print number of videos in the playlist
        print('Detected ' + str(playlist_len) + ' videos in the playlist.')
        #for each video in the playlist, request the video streams and select the best stream then downlad it
        for i in range(playlist_len):
            video = playlist.videos[i]
            ui_data.text('['+str(i+1)+'/'+str(playlist_len)+'] Retrieving stream information for: '+video.title)
            try:
                video_streams = video.streams
                thumbnail = video.thumbnail_url
                #select the best stream
                best_stream = video_streams.filter(progressive=True).order_by('resolution').desc().first()
                #add stream to a list of selected streams
                selected_streams.append(best_stream)
                #thumbnail_urls.append(thumbnail)
                #download the video   
            except Exception as e:
                print('Error: '+str(e))
                stream_errors.append(i+1)
                ui_error.error('Caught an error, skipping song number(s): '+str(stream_errors))
                continue
    elif 'watch' in config_data['link'] or 'v=' in config_data['link']:
        print('Link is a video.')
        #if the link contains a 'v='or 'watch' it's a video
        #create a video object from the link
        video = ytd.YouTube(config_data['link'])
        #request the video streams
        ui_data.text('Retrieving stream information for: '+video.title)
        thumbnail = video.thumbnail_url
        #get the video streams
        video_streams = video.streams.filter(progressive=True)
        #order the streams by the quality
        video_streams = video_streams.order_by('resolution').desc()
        #get the first stream in the list
        selected_stream = video_streams.first() 
        #save selected stream for download
        selected_streams.append(selected_stream)
        #thumbnail_urls.append(thumbnail)
    #otherwise the link is invalid and return empty streams
    else:
        print('Link is invalid. Nothing has been downloaded')
        selected_streams = None
    ui_data.empty()
    ui_status.empty()
    #returns a list of videos either from playlist or single video from the link
    #it is in a video list format
    print('Selected streams for download: '+ str(len(selected_streams)) + ' streams.')
    #create a dictionary with key streams and value the list of selected streams and key thumbnail and value the thumbnail url
    streams_thumbs = {'streams': selected_streams, 'thumbnails': thumbnail_urls}
    print('Streams and thumbnail urls: '+str(streams_thumbs))
    return streams_thumbs    
#####DEBUGGING#####
#load config file
config_data = ytd.load_config_file()
#override config data 
#config_data = ytd.set_link(config_data)

def run_app():
    #Build the UI
    hide_footer()
    #static header
    build_header()
    #
    build_dynamic(config_data)
    

#
def hide_footer():
    hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#to do 
#a function that takes a list of columns from the build download entry
#and as each file is downloaded then converted and organized
#it changes the colour of the id column cell to appropriate colour
#dark grey - prepared, blac - downloaded, orange - converting, green - organized
#red - error

#add a functionality to work with config files and config data
#interactions modify config data and save config file each time a value is changed
#download button will start analyzing and display general info about the link and the total download size
#then display the download list and start downloading

#fix aesthetics of the download postion title and size display



#add advanced settings to let user change the maximal number of downloaded songs