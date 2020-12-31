import socket
import struct
from threading import Thread
import threading
import time
import random
from scapy.arch import get_if_addr


GROUPS_DICT ={1:[],2:[]}
CONNECTIONS_DICT = {}

class server:
    def __init__(self, eth_num):
        self.UDP_PORT = 13107
        self.TCP_PORT = 13118
        self.BUFFER_SIZE = 1024
        self.GAME_ON = False
        self.CONNECTIONS_DICT = {}
        if eth_num == 1:
            self.IP_ADDRESS = get_if_addr("eth1")
        else:
            self.IP_ADDRESS = get_if_addr("eth2")
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.random_group_num = 0
        


    def run_udp(self):
        end_time = time.time() + 10
        broadcast_message = struct.pack('Ibh', 0xfeedbeef, 0x2, self.TCP_PORT)
        self.server_socket_udp.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        while time.time() < end_time:
            self.server_socket_udp.sendto(broadcast_message,('<broadcast>', self.UDP_PORT))
            time.sleep(1)
        self.GAME_ON = True
        self.server_socket_udp.close()

    def run_tcp(self):
        self.random_group_num = random.randint(1,2)
        print("Server started, listening on IP address "+str(self.IP_ADDRESS))
        self.server_socket_tcp.bind((self.IP_ADDRESS,self.TCP_PORT))
        self.server_socket_tcp.settimeout(0.5)
        self.server_socket_tcp.listen()
        while not self.GAME_ON:
            try:
                connection_socket, client_address = self.server_socket_tcp.accept()
                team_name = connection_socket.recv(self.BUFFER_SIZE)                
            except:
                continue

            team_name = team_name.decode("utf-8")
            self.random_casting_to_group(connection_socket, team_name, self.random_group_num)
            if self.random_group_num == 1:
                self.random_group_num = 2
            else:
                self.random_group_num = 1

        start_message = self.message_builder()
        for conn in self.CONNECTIONS_DICT.keys():
            conn.sendall(start_message.encode("utf-8"))
        self.run_the_game()
#       server_socket_tcp.close()
                       

    def run_the_game(self):
        self.run_all_listeners()
        team_1_score, team_2_score = self.calculate_score()
        game_summary_message = self.game_summary_builder(team_1_score, team_2_score)
        self.send_summary_message_to_players(game_summary_message)


    def calculate_score(self):
        team_1_score = 0
        team_2_score = 0
        for conn_lst in self.CONNECTIONS_DICT.values():
            if conn_lst[1] == 1:
                team_1_score += conn_lst[2] 
            else:
                team_2_score += conn_lst[2]
        return team_1_score, team_2_score

    def game_summary_builder(self, team_1_score, team_2_score):
        winner = ""
        if team_1_score > team_2_score:
            winner = "Group 1 wins!"
        elif team_2_score > team_1_score:
            winner = "Group 2 wins!"
        else:
            winner = "Its a tie"
        
        game_summary = "Game over!\n"
        game_summary += "Group 1 typed in {} characters.\n".format(team_1_score)
        game_summary += "Group 2 typed in {} characters.\n".format(team_2_score)
        game_summary += winner+"\n\n"

        if winner != "Its a tie":
            game_summary += "Congratulations to the winners:\n==\n"
            if winner == "Group 1 wins!":
                winners_names = self.get_teams_name_from_group(1)
            else:
                winners_names = self.get_teams_name_from_group(2)
            game_summary += winners_names
        return game_summary

    def send_summary_message_to_players(self, summary_message):
        for conn in self.CONNECTIONS_DICT.keys():
            conn.sendall(summary_message.encode("utf-8"))


    def run_all_listeners(self):
        list_of_players_threads = []
        list_of_stop_event = []
        for conn in self.CONNECTIONS_DICT.keys():
            stop_event = threading.Event()
            list_of_stop_event.append(stop_event)
            player_listen_thread = Thread(target=self.listen_to_player,args=(conn, stop_event, ))
            list_of_players_threads.append(player_listen_thread)
        for thread in list_of_players_threads:
            thread.start() 

        time.sleep(10)
        for stop_event in list_of_stop_event:
            stop_event.set()
        for thread in list_of_players_threads:
            thread.join()


    def listen_to_player(self, conn, stop_event):
        score = 0
        while not stop_event.is_set():
            try:
                conn.settimeout(2)
                conn.recv(BUFFER_SIZE)
                if stop_event.is_set():
                    break
                score += 1
            except:
                if stop_event.is_set():
                    break
        self.CONNECTIONS_DICT[conn][2] = score    

    def random_casting_to_group(self, connection_socket, team_name, group_num):
        score = 0
        self.CONNECTIONS_DICT[connection_socket] = [team_name, group_num, score]
    
    def message_builder(self):
        start_message = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
        group_1_names = self.get_teams_name_from_group(1)
        start_message += group_1_names
        group_2_names = self.get_teams_name_from_group(2)
        start_message +="Group 2:\n==\n"
        start_message += group_2_names
        start_message +="\nStart pressing keys on your keyboard as fast as you can!!"
        return start_message       

    def get_teams_name_from_group(self, group_num):
        names_in_group = ""
        for lst in self.CONNECTIONS_DICT.values():
            if lst[1] == group_num:
                names_in_group += lst[0]
        return names_in_group 

    def reset_server(self):
        self.CONNECTIONS_DICT = {}
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.random_group_num = 0

    def run_server(self):
        while True:
            udp_thread = Thread(target=self.run_udp)
            tcp_thread = Thread(target=self.run_tcp)
            udp_thread.start()
            tcp_thread.start()
            udp_thread.join()
            tcp_thread.join()
            time.sleep(1)
            self.reset_server()


if __name__ == "__main__":
    eth_num = 1
    server = server(eth_num)
    server.run_server()
