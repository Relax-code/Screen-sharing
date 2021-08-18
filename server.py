import pickle
import socket
import struct
import time
from multiprocessing import Process, Manager
from multiprocessing import Queue

import cv2
import numpy as np


def buffer_count(buffer: Queue):
    while True:
        if buffer.qsize() >= 5000:
            frame = buffer.get(block=False)
            time.sleep(0.5)
            cv2.imshow('frame', frame)
            cv2.waitKey(1)


def frame_executor(buffer: Queue):
    HOST = ''
    PORT = 8089

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    s.bind((HOST, PORT))
    print('Socket bind complete')
    s.listen(1)
    print('Socket now listening')

    conn, addr = s.accept()

    data = b''
    payload_size = struct.calcsize("L")

    while True:
        while len(data) < payload_size:
            data += conn.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        d = np.array(frame)
        buffer.put(d)
        print(buffer.qsize())


if __name__ == '__main__':

    processes = []
    m = Manager()
    buffer = m.Queue()
    proc1 = Process(target=frame_executor, args=(buffer,))
    proc2 = Process(target=buffer_count, args=(buffer,))

    processes.append(proc2)
    processes.append(proc1)

    proc1.start()
    proc2.start()

    for proc in processes:
        proc.join()
