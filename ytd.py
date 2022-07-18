import subprocess
import sys
import os

import ytdWebUI as GUI

#get current working directory
cwd = os.getcwd()
#get this file name
file_name = sys.argv[0]
#get the path of this file
file_path = cwd + "\\" + file_name
print('------->'+file_path)
command = '' #("streamlit run " + file_path)
os.system('"' + command + '"')
GUI.run_app()