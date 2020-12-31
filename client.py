import socket
import struct
import time
from threading import Thread
from curtsies import Input
from scapy.arch import get_if_addr
import ColorMessages
import random


class client:
    """
    client class for the Keyboard Spamming Battle Royale.
    """
    def __init__(self, team_name):
        """
        :param team_name: the client's them name 
        """
        self.MAGIC_COOKIE = hex(0xfeedbeef)
        self.MESSAGE_TYPE = hex(0x2)
        self.UDP_PORT = 13107
        self.IP_ADDRESS = get_if_addr("eth1")
        self.BUFFER_SIZE = 1024
        self.TEAM_NAME = team_name + "\n"
        self.GAME_ON = False
        self.client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_port = None
        self.server_ip = None
        self.client_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket_udp.bind(('', self.UDP_PORT))

    def listen_to_udp(self):
        """
        method to recieve offers from the server.
        """
        while True:
            msg , server_address  = self.client_socket_udp.recvfrom(self.BUFFER_SIZE)
            print("Received offer from " + ColorMessages.red + str(server_address[0]) + ColorMessages.reset + " attempting to connect...​")
            msg_unpacked = struct.unpack("Ibh", msg)
            if hex(msg_unpacked[0]) == self.MAGIC_COOKIE and hex(msg_unpacked[1]) == self.MESSAGE_TYPE:
                self.tcp_server_port = msg_unpacked[2]
                self.server_ip = server_address[0]
                self.connect_to_server_tcp()
                break          

    def connect_to_server_tcp(self):
        """
        connect to the server via tcp
        """
        self.client_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_tcp.connect((self.server_ip, self.tcp_server_port))
        self.client_socket_tcp.sendall(self.TEAM_NAME.encode("utf-8"))
    
    def wait_for_start_game(self):
        """
        get the message that the game is starting
        """
        start_message = self.client_socket_tcp.recv(self.BUFFER_SIZE)
        start_message_decoded = start_message.decode("utf-8")
        msg_to_print = ""
        for msg_char in start_message_decoded:
            if msg_char == " " or msg_char == "\n":
                msg_to_print += msg_char
            else:
                num_of_color = random.randint(0, len(ColorMessages.colors) - 1)
                msg_to_print += ColorMessages.colors[num_of_color] + msg_char + ColorMessages.reset
        print(msg_to_print)
        self.GAME_ON = True

    def listen_to_server(self):
        """
        while the game is on, the cliect listen to server that will send him when the game is over.
        in addition, the client gets here the game summary message and print it.
        """
        while True:
            end_message = self.client_socket_tcp.recv(self.BUFFER_SIZE)
            if end_message.decode("utf-8") == "Game Over" or len(end_message.decode("utf-8")) == 0:
                self.GAME_ON = False
                break
        summary_message = self.client_socket_tcp.recv(self.BUFFER_SIZE)
        summary_message_decoded = summary_message.decode("utf-8")
        msg_to_print = ""
        for msg_char in summary_message_decoded:
            if msg_char == " " or msg_char == "\n":
                msg_to_print += msg_char
            else:
                num_of_color = random.randint(0, len(ColorMessages.colors) - 1)
                msg_to_print += ColorMessages.colors[num_of_color] + msg_char + ColorMessages.reset
        print(msg_to_print)


    def listen_to_keyboard(self):
        """
        the client listen to the keyboard to get keyboard pressing.
        """
        with Input(keynames='curtsies') as input_generator:
            while self.GAME_ON:
                key = input_generator.send(0.5)
                if key is None:
                    continue
                else:
                    self.on_press(key)

    def on_press(self, key):
        """
        send to the server that the key pressed.
        :param key: the key that the client pressed on
        """
        try:
            self.client_socket_tcp.sendall("{}".format(key).encode("utf-8"))
        except:
            print("Connection lost ...\n")
            raise Exception

    def play(self):
        """
        in 1 thread the client listening to the server and in the main thread listening to keyboard.
        """
        listen_to_server_thread = Thread(target=self.listen_to_server)
        listen_to_server_thread.start()
        self.listen_to_keyboard()
        listen_to_server_thread.join()
    
    def reset_client(self):
        """
        reset the client and the necessary attributes
        """
        self.GAME_ON = False
        self.tcp_server_port = None
        self.server_ip = None

    def run_client(self):
        """
        main method of the client.
        at the end of each loop, the client reset.
        """
        while True:
            try:
                print("​Client started, listening for offer requests...​")
                self.listen_to_udp()
                self.wait_for_start_game()
                self.play()
                print("Server disconnected, listening for offer requests...")
                self.reset_client()

            except:
                self.reset_client()
                

        
if __name__ == "__main__":
    team_name = "Happy NoviGod"
    client = client(team_name)
    client.run_client()
