from bilibili_spider import BILI
import threading
import time
import os
import json
import shutil
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
        # line = '4912937'
        if line in record:
            if type(record[line]) is int and record[line] is 1:
                record[line] = [1, 1]
                continue
            if type(record[line]) is list and record[line][1] is 1:
                continue
            if (type(record[line]) is int and record[line] == 0 or type(record[line]) is list and record[line][1] == 0) and os.path.exists('dataset/' + line):
                shutil.rmtree('dataset/' + line)


        print('Now:', line)
        b = BILI(line)
        if b.finished == True:
            record[line] = [b.videolength, 1]
        else:
            record[line] = [b.videolength, 0]

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
