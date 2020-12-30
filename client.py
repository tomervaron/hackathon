import socket
import struct
import time
from threading import Thread
from curtsies import Input
from scapy.arch import get_if_addr

MAGIC_COOKIE = hex(0xfeedbeef)
MESSAGE_TYPE = hex(0x2)
UDP_PORT = 13107
IP_ADDRESS = get_if_addr("eth1")
BUFFER_SIZE = 1024
TEAM_NAME = "Team MiniMax" + "\n"


def on_press(key):
    try:
        client_socket_tcp.sendall("{}".format(key).encode("utf-8"))
    except:
        pass

while True:
    client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("​Client started, listening for offer requests...​")
    client_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # client_socket_udp.bind(('', UDP_PORT))
    # break
    while True:
        try:
            client_socket_udp.bind(('', UDP_PORT))
            break
        except:
            time.sleep(0.1)
            continue
    
    # client_socket_udp.settimeout(200) #to remove

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
                client_socket_tcp.sendall(TEAM_NAME.encode("utf-8"))
                client_socket_udp.close()
            except:
                continue
            msg = client_socket_tcp.recv(BUFFER_SIZE)
            end_time = time.time() + 10
            print(msg.decode("utf-8"))

            with Input(keynames='curtsies') as input_generator:
                while time.time() < end_time:
                    e = input_generator.send(1)
                    if e is None:
                        continue
                    else:
                        on_press(e)
                game_summary = client_socket_tcp.recv(BUFFER_SIZE)
                print(game_summary.decode("utf-8"))

            break #to remove
    client_socket_tcp.close()
    print("Server disconnected, listening for offer requests...")
