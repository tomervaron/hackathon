import socket
import struct
import time
from threading import Thread
# from curtsies import Input
import getch
# import pygame

MAGIC_COOKIE = hex(0xfeedbeef)
MESSAGE_TYPE = hex(0x2)
UDP_PORT = 13117
BUFFER_SIZE = 1024

client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def on_press(key):
    try:
        client_socket_tcp.sendall("{}".format(key).encode("utf-8"))
    except:
        pass


print("​Client started, listening for offer requests...​")
client_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client_socket_udp.bind(('', UDP_PORT))
client_socket_udp.settimeout(200) #to remove

while True:
    msg , server_address  = client_socket_udp.recvfrom(BUFFER_SIZE)
    msg = struct.pack('Ibh', 0xfeedbeef, 0x2, 0x333e)
    print("Received offer from " + str(server_address[0]) + " attempting to connect...​")

    msg_unpacked = struct.unpack("Ibh", msg)
    if hex(msg_unpacked[0]) == MAGIC_COOKIE and hex(msg_unpacked[1]) == MESSAGE_TYPE:
        tcp_server_port = msg_unpacked[2]
        server_ip = server_address[0]
        try:
            client_socket_tcp.connect((server_ip, tcp_server_port))
        except:
            continue
        client_socket_tcp.sendall("Team Rocket\n".encode("utf-8"))
        client_socket_udp.close()
        msg = client_socket_tcp.recv(BUFFER_SIZE)
        print(msg.decode("utf-8"))
        end_time = time.time() + 10

        with Input(keynames='curtsies') as input_generator:
            for e in Input():
                if time.time() >= end_time:
                    break
                else:
                    on_press(e)
        # while time.time()<end_time:
        #     c = getch.getch()
        #     on_press(c)

        # with keyboard.Listener(on_press=on_press, suppress=True) as listener:
        #     def time_out(time_to_run: int):
        #         time.sleep(time_to_run)
        #         listener.stop()
               
        #     Thread(target=time_out, args=(10,), ).start()
        #     listener.join()

        break
client_socket_tcp.close()
print("client is close")
