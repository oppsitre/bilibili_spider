from bilibili_spider import BILI
import threading
import time
exitFlag = 0
class myThread (threading.Thread):
    def __init__(self, aid):
        threading.Thread.__init__(self)
        self.aid = aid
    def run(self):
        print("Starting " + self.aid)
        print_time(self.aid)
        print("Exiting " + self.aid)

def print_time(aid):
    b = BILI(aid)

if __name__ == '__main__':
    thd = []
    for line in open('video.csv'):
        line = line.strip()
        thd.append(myThread(line))

    for t in thd:
        t.start()
