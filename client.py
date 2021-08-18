import socket
import pickle
import struct

from PIL import ImageGrab

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))

while True:
    img = ImageGrab.grab(bbox=(100, 50, 1920, 1280))
    data = pickle.dumps(img)
    message_size = struct.pack("L", len(data))
    clientsocket.sendall(message_size + data)
