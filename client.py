import logging
import socket
import _pickle as cpk
import _struct as cstruct
import zlib
import time
import multiprocessing
from multiprocessing import Queue

import mss
from mss.base import ScreenShot


class Client:

    @staticmethod
    def send_frame_to_socket(client, buffer):
        while True:
            if buffer.qsize() >= 10:
                data = buffer.get(block=False)
                print("Sending data...")
                client.sendall(data)
            else:
                time.sleep(0.01)


class DataConverter:

    @staticmethod
    def compress_data(data: bytes) -> bytes:
        return zlib.compress(data, level=1)

    @staticmethod
    def struct_data(compress_data: bytes) -> bytes:
        return cstruct.pack("L", len(compress_data))

    @staticmethod
    def convert_img_to_bytes(img: ScreenShot):
        return cpk.dumps(img)

    @staticmethod
    def get_img_from_queue(queue: Queue):
        while True:
            if queue.qsize() >= 10:
                return queue.get(block=False)
            else:
                time.sleep(0.01)

    def run(self, images: Queue, buffer: Queue):
        while True:
            now = time.time()
            img = self.get_img_from_queue(images)
            print("Img recv")
            bytes_img = self.convert_img_to_bytes(img)
            compress_data = self.compress_data(bytes_img)
            message_size = self.struct_data(compress_data)
            print("Data sending to buffer...")
            buffer.put(message_size + compress_data, block=False)
            print(time.time() - now)


class ScreenShotGenerator:
    @staticmethod
    def put_screenshot_to_buffer(queue: Queue):
        src = mss.mss()
        monitor = {'top': 0, 'left': 0, 'width': 720, 'height': 480}
        while True:
            img = src.grab(monitor)
            print("Img sending to queue...")
            queue.put(img, block=False)


if __name__ == '__main__':
    m = multiprocessing.Manager()
    queue_with_img = m.Queue()
    queue_with_data = m.Queue()
    client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_conn.connect(('localhost', 8089))

    processes = []

    ssg = ScreenShotGenerator()
    screen_shot_gen_proc = multiprocessing.Process(target=ssg.put_screenshot_to_buffer, args=(queue_with_img,))
    screen_shot_gen_proc.start()
    processes.append(screen_shot_gen_proc)
    print("Screenshot started...")

    converter = DataConverter()
    for i in range(2):
        print(f"Converted {i} started...")
        process = multiprocessing.Process(target=converter.run, args=(queue_with_img, queue_with_data))
        processes.append(process)
        process.start()

    client = Client()
    client_process = multiprocessing.Process(target=client.send_frame_to_socket, args=(client_conn, queue_with_data,))
    client_process.start()
    processes.append(client_process)
    print(f"Client started...")

    for process in processes:
        process.join()
