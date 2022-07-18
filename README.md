# SimpleYouTubeDownloader
A compact and simple youtube downloader based on pyvideo and pytube, it lets the user input a link to a playlist or a video, select format (mp3/mp4) and save directory and download the video. For mp3 selection the videos are downloaded then converted to mp3. 


# Running
You need to install dependencies: moviepy, pytube, streamlit, pandas, tkinter, blinker 

# Use command:
pip install moviepy pytube streamlit pandas tkinter blinker

# To run GUI navigate to the folder 
cd [path]

# and run the ytd.py with streamlit using command:
streamlit run ytd.py

# GUI will show
![image](https://user-images.githubusercontent.com/56128558/179621398-12c87265-6e93-4501-ae74-53409f9178d1.png)
After inputing information press "Analyze and download".

The link will be resolved and data requested from YouTube
![image](https://user-images.githubusercontent.com/56128558/179621800-4f93b59a-6907-49f5-bdee-d80491fd0c9a.png)

Then videos will be downloaded
![image](https://user-images.githubusercontent.com/56128558/179621916-5a4b06bd-0ee0-4293-b5dc-ff3f056924a9.png)
If there's a problem with a video in a playlist, the downloader will skip to the next song and notify which song number needs to be redone
![image](https://user-images.githubusercontent.com/56128558/179622078-007eab79-019e-401f-ad00-42255690d743.png)

Then if necessary videos are covnerted converted
![image](https://user-images.githubusercontent.com/56128558/179622180-bfeee939-e004-445e-ba97-b7f068d503eb.png)


This is an early version, with basic GUI written in streamline, with little modification it can be used to create a local-running software. 
Just needs a different GUI.


# Bugs
it doesn't work with short links youtu.be
with very long playlists it can get stuck (might be some protection from YT)
