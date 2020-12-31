# import socket
# import struct
# from threading import Thread
# import threading
# import time
# import random
# from scapy.arch import get_if_addr


# UDP_PORT = 13107
# TCP_PORT = 13118
# BUFFER_SIZE = 1024
# #IP_ADDRESS = socket.gethostbyname(socket.gethostname())
# IP_ADDRESS = get_if_addr("eth1")
# groups_dict ={1:[],2:[]}
# connections_dict = {}


# def random_casting_to_group(connection_socket, team_name):
#     group_num = random.randint(1,2)
#     if group_num == 1:
#         if len(groups_dict[1]) > 0 and len(groups_dict[2]) == 0:
#             # groups_dict[2].append((connection_socket, team_name))
#             groups_dict[2].append([team_name, 0])
#         else:
#             #  groups_dict[1].append((connection_socket, team_name))
#             groups_dict[1].append([team_name, 0])
#     else:
#         if len(groups_dict[2]) > 0 and len(groups_dict[1]) == 0:
#             # groups_dict[1].append((connection_socket, team_name))
#             groups_dict[1].append([team_name, 0])
#         else:
#             # groups_dict[2].append((connection_socket, team_name))
#             groups_dict[2].append([team_name, 0])


# def get_teams_name(num_of_group):
#     names = ""
#     for tup in groups_dict[num_of_group]:
#         names+=tup[0]+"\n"
#     return names

# def get_team_name_via_conn(conn):
#     names = ""
#     for num_of_group in groups_dict.keys():
#         for tup in groups_dict[num_of_group]:
#             if tup[0] == conn:
#                 names+=tup[1]
#     return names
    
# def message_builder():
#     to_return = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
#     group_1_names = get_teams_name(1)
#     to_return += group_1_names
#     group_2_names = get_teams_name(2)
#     to_return +="Group 2:\n==\n"
#     to_return += group_2_names
#     to_return +="\nStart pressing keys on your keyboard as fast as you can!!"
#     return to_return

# def play_the_game():
#     list_of_players_threads = []
#     list_of_stop_event = []
#     print("Game started!\n")
#     for conn in connections_dict.keys():
#         stop_event = threading.Event()
#         list_of_stop_event.append(stop_event)
#         player_listen_thread = Thread(target=player_listener,args=(conn, stop_event, ))
#         list_of_players_threads.append(player_listen_thread)
#     for thread in list_of_players_threads:
#         thread.start() 

#     time.sleep(10)
#     for stop_event in list_of_stop_event:
#         stop_event.set()
#     for thread in list_of_players_threads:
#         thread.join()
    
#     # for conn in connections_dict.keys():
#     #     print("{} score: {}\n".format(get_team_name_via_conn(conn),connections_dict[conn][1]))
    
#     team_1_score = 0
#     for tup in groups_dict[1]:
#         # team_1_score += connections_dict[tup[0]][1]
#         team_1_score += tup[1]
#         # team_1_score += connections_dict[tup][1]
    
#     team_2_score = 0
#     for tup in groups_dict[2]:
#         # team_2_score += connections_dict[tup[0]][1]
#         team_2_score += tup[1]
#         # team_2_score += connections_dict[tup][1]

#     winner = ""
#     if team_1_score > team_2_score:
#         winner = "Group 1 wins!"
#     elif team_2_score > team_1_score:
#         winner = "Group 2 wins!"
#     else:
#         winner = "Its a tie"
    
#     game_summary = "Game over!\n"
#     game_summary += "Group 1 typed in {} characters.\nGroup 2 typed in {} characters.\n".format(team_1_score,team_2_score)
#     game_summary += winner+"\n\n"

#     if winner != "Its a tie":
#         game_summary += "Congratulations to the winners:\n==\n"
#         if winner == "Group 1 wins!":
#             winners_names = get_teams_name(1)
#         else:
#             winners_names = get_teams_name(2)
#         game_summary += winners_names
    
#     # print(game_summary)
#     # connections_key_list = list(connections_dict.keys())
#     # lost_counter = 0
#     # while len(connections_key_list) > 0:
#     #     try:
#     #         connections_key_list[0].sendall(game_summary.encode("utf-8"))
#     #         connections_key_list.pop(0)
#     #         lost_counter = 0
#     #     except:
#     #         lost_counter += 1
#     #         if lost_counter == 3: # trying to send the message 3 times
#     #             print("lost connection with " + str(connections_dict[connections_key_list[0]][0][0]) +"\n")
#     #             connections_key_list.pop(0)
#     #             lost_counter = 0
            

#         for conn in connections_dict.keys():
#             conn.sendall(game_summary.encode("utf-8"))
        
        


# def player_listener(conn, stop_event):
#     score = 0
#     while not stop_event.is_set():
#         try:
#             conn.settimeout(2)
#             conn.recv(BUFFER_SIZE)
#             if stop_event.is_set():
#                 break
#             score += 1
#         except:
#             if stop_event.is_set():
#                 break
#     # connections_dict[conn][1] = score
#     team_name = connections_dict[conn][2]
#     for group in groups_dict:
#         for name_n_score in groups_dict[group]:
#             if name_n_score[0] == team_name:
#                 groups_dict[group][1] = score
#                 break



# def send_udp():
#     server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     message = struct.pack('Ibh', 0xfeedbeef, 0x2, TCP_PORT)
#     server_socket_udp.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
#     # server_socket_udp.bind((IP_ADDRESS,UDP_PORT))
#     end_time = time.time() + 10
#     while time.time() < end_time:
#         server_socket_udp.sendto(message,(IP_ADDRESS, UDP_PORT))
#         time.sleep(1)
#     server_socket_udp.close()

# def run_tcp_socket():
#     end_time = time.time() + 10
#     server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     print("Server started, listening on IP address "+str(IP_ADDRESS))
#     while True:
#         try:
#             server_socket_tcp.bind((IP_ADDRESS,TCP_PORT))
#             break
#         except:
#             continue
    
#     server_socket_tcp.settimeout(10) # to remove
#     server_socket_tcp.listen()

#     groups_dict ={1:[],2:[]}
#     connections_dict = {}
#     while True:
#         try:
#             # try:
#             #     connection_socket, client_address = server_socket_tcp.accept()
#             # except:
#             #     if time.time() >= end_time:
#             #         raise
#             #     continue
#             connection_socket, client_address = server_socket_tcp.accept()
#             team_name = connection_socket.recv(BUFFER_SIZE)
#             connections_dict[connection_socket] = [client_address,0,team_name]
#             print (len(connections_dict))
#             # connection_socket
#             team_name = team_name.decode("utf-8")[:-1]
#             random_casting_to_group(connection_socket, team_name)
#         except:
#             if time.time() < end_time:
#                 continue
#             break
#     message_to_send = message_builder()
#     for conn in connections_dict.keys():
#         connections_key_list = list(connections_dict.keys())
#         lost_counter = 0
#         while len(connections_key_list) > 0:
#             try:
#                 connections_key_list[0].sendall(message_to_send.encode("utf-8"))
#                 connections_key_list.pop(0)
#                 lost_counter = 0
#             except:
#                 lost_counter += 1
#                 if lost_counter == 3: # trying to send the message 3 times
#                     print("lost connection with " + str(connections_dict[connections_key_list[0]][0][0]) +"\n")
#                     connections_key_list.pop(0)
#                     lost_counter = 0
#     play_the_game()
#     time.sleep(2)
#     server_socket_tcp.close()
#     print("\nGame over, sending out offer requests...\n")
#     # break

# i=0
# while i<1:    
#     udp_thread = Thread(target=send_udp)
#     tcp_thread = Thread(target=run_tcp_socket)
#     udp_thread.start()
#     tcp_thread.start()
#     udp_thread.join()
#     tcp_thread.join()
#     i += 1


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
        while time.time() < end_time:
            broadcast_message = struct.pack('Ibh', 0xfeedbeef, 0x2, self.TCP_PORT)
            self.server_socket_udp.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
            self.server_socket_udp.sendto(broadcast_message,('<broadcast>', UDP_PORT))
            time.sleep(1)
        server_socket_udp.close()

    def run_tcp(self):
        self.random_group_num = random.randint(1,2)
        print("Server started, listening on IP address "+str(IP_ADDRESS))
        self.server_socket_tcp.bind(('',self.TCP_PORT))
        self.server_socket_tcp.settimeout(0.5)
        self.server_socket_tcp.listen()
        while True:
            try:
                connection_socket, client_address = self.server_socket_tcp.accept()
                team_name = connection_socket.recv(self.BUFFER_SIZE)                
            except:
                continue

            team_name = team_name.decode("utf-8")
            random_casting_to_group(connection_socket, team_name, self.random_group_num)
            if self.random_group_num == 1:
                self.random_group_num = 2
            else:
                self.random_group_num = 1
            start_message = message_builder()
            for conn in self.CONNECTIONS_DICT.keys():
                conn.sendall(start_message.encode("utf-8"))
            run_the_game()
#             server_socket_tcp.close()
            break            

    def run_the_game(self):
        run_all_listeners()
        team_1_score, team_2_score = calculate_score()
        game_summary_message = game_summary_builder(team_1_score, team_2_score)
        send_summary_message_to_players(game_summary_message)


    def calculate_score(self):
        team_1_score = 0
        team_2_score = 0
        for conn_lst in self.CONNECTIONS_DICT.values():
            if conn_lst[1] == 1:
                team_1_score += lst[2] 
            else:
                team_2_score += lst[2]
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
                winners_names = get_teams_name_from_group(1)
            else:
                winners_names = get_teams_name_from_group(2)
            game_summary += winners_names
        return game_summary

    def send_summary_message_to_players(self, summary_message):
        for conn in self.CONNECTIONS_DICT.keys():
            conn.sendall(game_summary.encode("utf-8"))


    def run_all_listeners(self):
        list_of_players_threads = []
        list_of_stop_event = []
        for conn in self.CONNECTIONS_DICT.keys():
            stop_event = threading.Event()
            list_of_stop_event.append(stop_event)
            player_listen_thread = Thread(target=listen_to_player,args=(conn, stop_event, ))
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
        group_1_names = get_teams_name_from_group(1)
        start_message += group_1_names
        group_2_names = get_teams_name_from_group(2)
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
            udp_thread = Thread(target=run_udp)
            tcp_thread = Thread(target=run_tcp)
            udp_thread.start()
            tcp_thread.start()
            udp_thread.join()
            tcp_thread.join()
            time.sleep(1)
            reset_server()


if __name__ == "__main__":
    eth_num = 1
    server = server(eth_num)
    server.run_server()


############################### from git ############################## working partly

# import socket
# import struct
# from threading import Thread
# import threading
# import time
# import random


# UDP_PORT = 13107
# TCP_PORT = 13118
# BUFFER_SIZE = 1024
# IP_ADDRESS = socket.gethostbyname(socket.gethostname())
# groups_dict ={1:[],2:[]}
# connections_dict = {}


# def get_teams_name(num_of_group):
#     names = ""
#     for tup in groups_dict[num_of_group]:
#         names+=tup[1]+"\n"
#     return names

# def get_team_name_via_conn(conn):
#     names = ""
#     for num_of_group in groups_dict.keys():
#         for tup in groups_dict[num_of_group]:
#             if tup[0] == conn:
#                 names+=tup[1]
#     return names
    
# def message_builder():
#     to_return = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
#     group_1_names = get_teams_name(1)
#     to_return += group_1_names
#     group_2_names = get_teams_name(2)
#     to_return +="Group 2:\n==\n"
#     to_return += group_2_names
#     to_return +="\nStart pressing keys on your keyboard as fast as you can!!"
#     return to_return

# def play_the_game():
#     list_of_players_threads = []
#     list_of_stop_event = []
#     for conn in connections_dict.keys():
#         stop_event = threading.Event()
#         list_of_stop_event.append(stop_event)
#         player_listen_thread = Thread(target=player_listener,args=(conn, stop_event, ))
#         list_of_players_threads.append(player_listen_thread)
#     for thread in list_of_players_threads:
#         thread.start() 

#     time.sleep(10)
#     for stop_event in list_of_stop_event:
#         stop_event.set()
#     for thread in list_of_players_threads:
#         thread.join()
    
#     for conn in connections_dict.keys():
#         print("{} score: {}\n".format(get_team_name_via_conn(conn),connections_dict[conn][1]))

#     team_1_score = 0
#     for tup in groups_dict[1]:
#         team_1_score += connections_dict[tup[0]][1]
    
#     team_2_score = 0
#     for tup in groups_dict[2]:
#         team_2_score += connections_dict[tup[0]][1]
    
#     winner = ""
#     if team_1_score > team_2_score:
#         winner = "Group 1 wins!"
#     elif team_2_score > team_1_score:
#         winner = "Group 2 wins!"
#     else:
#         winner = "Its a tie"
    
#     game_summary = "Game over!\n"
#     game_summary += "Group 1 typed in {} characters.\nGroup 2 typed in {} characters.\n".format(team_1_score,team_2_score)
#     game_summary += winner+"\n\n"

#     if winner != "Its a tie":
#         game_summary += "Congratulations to the winners:\n==\n"
#         if winner == "Group 1 wins!":
#             winners_names = get_teams_name(1)
#         else:
#             winners_names = get_teams_name(2)
#         game_summary += winners_names
    
#     print(game_summary)
#     for conn in connections_dict.keys():
#         conn.sendall(game_summary.encode("utf-8"))


# def player_listener(conn, stop_event):
#     score = 0
#     while not stop_event.is_set():
#         try:
#             conn.settimeout(2)
#             conn.recv(BUFFER_SIZE)
#             if stop_event.is_set():
#                 break
#             score += 1
#         except:
#             if stop_event.is_set():
#                 break
#     connections_dict[conn][1] = score



# def send_udp():
#     server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     end_time = time.time() + 10
#     while  time.time() < end_time:
#         message = struct.pack('Ibh', 0xfeedbeef, 0x2, TCP_PORT)
#         server_socket_udp.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
#         server_socket_udp.sendto(message,('<broadcast>', UDP_PORT))
#         time.sleep(1)
#     server_socket_udp.close()

# def run_tcp_socket():
#     server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     print("Server started, listening on IP address "+str(IP_ADDRESS))
#     server_socket_tcp.bind(('',TCP_PORT))
#     server_socket_tcp.settimeout(10) # to remove
#     server_socket_tcp.listen(4)

#     while True:
#         try:
#             connection_socket, client_address = server_socket_tcp.accept()
#             team_name = connection_socket.recv(BUFFER_SIZE)
#             connections_dict[connection_socket] = [client_address,0]
#             team_name = team_name.decode("utf-8")[:-1]
#             random_casting_to_group(connection_socket, team_name)
#         except:
#             message_to_send = message_builder()
#             for conn in connections_dict.keys():
#                 conn.sendall(message_to_send.encode("utf-8"))
#             play_the_game()
#             server_socket_tcp.close()
#             break


    
# udp_thread = Thread(target=send_udp)
# tcp_thread = Thread(target=run_tcp_socket)
# udp_thread.start()
# tcp_thread.start()
# udp_thread.join()
# tcp_thread.join()