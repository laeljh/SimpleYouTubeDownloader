

'''
A simple YouTube downloader.
It uses a config file with the following information separated by  commas:
the video link, the format, save directory

The config file will be created if it does not exist with preset values.

The config file values will be read and populated into the app.

Whenever a value is changed, the config file will be updated.


Streamlit is used to create a web interface for the app.
It will have the following elements:
- A title and subtitle
- A text input for the video link or the playlist link
- A dropdown menu for the format
- A text input for the save directory, and a button to select a directory
- A download button


When a download is requested, the app will check if the link is a playlist or a video.
Then depending on the type, for each video it will:
1. request the video info from YouTube
2. display the video info and show a cancel button
3. show a progress bar while the video is downloading
4. download the video in the selected directory
-5. if the format is mp3, convert the video to mp3 using ffmpeg
-6. delete the original video file leaving only the converted mp3 file


#TO DO LATER:
Add functionality to run the program on a server and let user download the files from the server
Add functionality that allows user to input "serverIP/video_link" into the address bar and begin download


'''
#TO DO NOW
#add somehow the pause between download and confirmation
#fix download list display (make it collapsible and disapear completely after the download is confirmed)
#remove info 'depending on the size'
#and as soon as the button "analyze" is clicked until something is dispayed show loading timer animation


#add ability to skip songs that cause errors, remember the song number and try again