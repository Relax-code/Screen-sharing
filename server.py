import _pickle as pickle
import socket
import _struct as struct
import time
import zlib

import cv2
import numpy as np


def frame_executor():
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
        now = time.time()
        while len(data) < payload_size:
            data += conn.recv(4096*30)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += conn.recv(4096*30)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        try:
            frame = pickle.loads(zlib.decompress(frame_data))
        except Exception as e:
            print(e)
        d = np.array(frame)
        cv2.imshow('frame', d)
        cv2.waitKey(1)
        print(time.time() - now)


if __name__ == '__main__':
    frame_executor()
