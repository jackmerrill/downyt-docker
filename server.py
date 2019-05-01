from flask import Flask, g, session, redirect, request, url_for, jsonify, render_template, send_file, send_from_directory
import os
import subprocess
import youtube_dl
import glob
import time

app = Flask(__name__)
app.debug = True

message=None

def remove(path):
    """
    Remove the file or directory
    """
    if os.path.isdir(path):
        try:
            os.rmdir(path)
        except OSError:
            print("Unable to remove folder: {}".format(path))
    else:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            print("Unable to remove file: {}".format(path))
 
#----------------------------------------------------------------------
def cleanup(number_of_days, path):
    """
    Removes files from the passed in path that are older than or equal 
    to the number_of_days
    """
    time_in_secs = time.time() - (number_of_days * 24 * 60 * 60)
    for root, dirs, files in os.walk(path, topdown=False):
        for file_ in files:
            full_path = os.path.join(root, file_)
            stat = os.stat(full_path)
 
            if stat.st_mtime <= time_in_secs:
                remove(full_path)
 
        if not os.listdir(root):
            remove(root)

from datetime import datetime
from threading import Timer

x=datetime.today()
y=x.replace(day=x.day+1, hour=1, minute=0, second=0, microsecond=0)
delta_t=y-x

secs=delta_t.seconds+1

t = Timer(secs, cleanup(1, "dl/"))
t.start()

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'outtmpl': '../dl/%(title)s.%(ext)s',
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
}

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        link = request.form.get('Link')
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            video_url = info_dict.get("url", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)
            ydl.download([link])
        print("sending file...")
        return send_file("../dl/"+video_title+".mp4", as_attachment=True)
    else:
        return render_template("index.html", message=message)

@app.route('/dl/<id>', methods=["GET", "POST"])
def watch(id):
    if request.method == "GET":
        link = "https://youtube.com/"+id
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            video_url = info_dict.get("url", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)
            ydl.download([link])
        return send_file(video_title+"-"+video_id+".mp4", as_attachment=True)
    else:
        return render_template("index.html", message=message)


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=80)
    # app.run(host=os.environ['IP'], port=os.environ['PORT'], debug=True)
