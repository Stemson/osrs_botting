#woodcutter.py & 
#woodcutter - Vithala.py
import fishing
import woodcutter
import subprocess
import os
from threading import Thread

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def start_bot(filename):
    subprocess.run(filename, shell=True)

filenames = ["fishing.py","woodcutter.py"]

#t=Thread(target=start_bot, args=["woodcutter.py",])
#t.start()
threads = []

for filename in filenames:
    threads.append(Thread(target=start_bot, args=[filename,]))

for thread in threads:
    thread.start()
