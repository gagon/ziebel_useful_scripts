
import logging
import sys
import time
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(level=logging.ERROR)

class MyEventHandler(FileSystemEventHandler):
    def __init__(self, observer, fileext):
        self.observer = observer
        self.fileext = fileext

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(self.fileext):
            parse_ddfdata(event.src_path)


def run_watchdog(path,fileext):
    observer = Observer()
    event_handler = MyEventHandler(observer, fileext)
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    observer.join()
    return 0


def parse_ddfdata(f):

    ddf_file=open(f,'r')
    depth=[]
    temp=[]
    for line in ddf_file:
        depth.append(line.split(",")[0])
        temp.append(line.split(",")[1])
    print "==========================="


if __name__ == "__main__":
    
    
        
    
    
    path=r"C:\Users\bolatzh\Documents\testing"
    run_watchdog(path,"txt")
