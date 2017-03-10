from bilibili_spider import BILI
import threading
import time
import os
import json
exitFlag = 0
class myThread (threading.Thread):
    def __init__(self, aid):
        threading.Thread.__init__(self)
        self.aid = aid
    def run(self):
        print("Starting " + self.aid)
        b = BILI(self.aid)
        print("Exiting " + self.aid)


def fileCountIn(dir):
    return sum([len(files) for root,dirs,files in os.walk(dir)])

if __name__ == '__main__':
    thd = []
    with open('record.json', 'r') as f:
        record = json.load(f)
    # record = {}
    for line in open('video_list.csv'):
        line = line.strip()
        if line in record and (record[line] == 1 or record[line] == 0):
            continue
        if os.path.exists('dataset/' + line) and fileCountIn('dataset/' + line) >= 6:
            if not(line in record.keys()):
                record[line] = 1
            continue

        b = BILI(line)
        if b.finished == True:
            record[line] = 1
        else:
            record[line] = 0

        with open('record.json', 'w') as f:
            json.dump(record, f)


    #     thd.append(myThread(line))
    #
    # for t in thd:
    #     t.start()
    #     while True:
    #         if(len(threading.enumerate()) < 2):
    #             break
    #
    # for t in thd:
    #     t.join()
