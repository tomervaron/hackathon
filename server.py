import socket
import struct
from threading import Thread
import threading
import time
import random


UDP_PORT = 13107
TCP_PORT = 13118
BUFFER_SIZE = 1024
IP_ADDRESS = socket.gethostbyname(socket.gethostname())
groups_dict ={1:[],2:[]}
connections_dict = {}


def random_casting_to_group(connection_socket, team_name):
    group_num = random.randint(1,2)
    if group_num == 1:
        if len(groups_dict[1]) > 0 and len(groups_dict[2]) == 0:
            groups_dict[2].append((connection_socket, team_name))
        else:
             groups_dict[1].append((connection_socket, team_name))
    else:
        if len(groups_dict[2]) > 0 and len(groups_dict[1]) == 0:
            groups_dict[1].append((connection_socket, team_name))
        else:
            groups_dict[2].append((connection_socket, team_name))


def get_teams_name(num_of_group):
    names = ""
    for tup in groups_dict[num_of_group]:
        names+=tup[1]+"\n"
    return names

def get_team_name_via_conn(conn):
    names = ""
    for num_of_group in groups_dict.keys():
        for tup in groups_dict[num_of_group]:
            if tup[0] == conn:
                names+=tup[1]
    return names
    
def message_builder():
    to_return = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
    group_1_names = get_teams_name(1)
    to_return += group_1_names
    group_2_names = get_teams_name(2)
    to_return +="Group 2:\n==\n"
    to_return += group_2_names
    to_return +="\nStart pressing keys on your keyboard as fast as you can!!"
    return to_return

def play_the_game():
    list_of_players_threads = []
    list_of_stop_event = []
    print("Game started!\n")
    for conn in connections_dict.keys():
        stop_event = threading.Event()
        list_of_stop_event.append(stop_event)
        player_listen_thread = Thread(target=player_listener,args=(conn, stop_event, ))
        list_of_players_threads.append(player_listen_thread)
    for thread in list_of_players_threads:
        thread.start() 

    time.sleep(10)
    for stop_event in list_of_stop_event:
        stop_event.set()
    for thread in list_of_players_threads:
        thread.join()
    
    # for conn in connections_dict.keys():
    #     print("{} score: {}\n".format(get_team_name_via_conn(conn),connections_dict[conn][1]))

    team_1_score = 0
    for tup in groups_dict[1]:
        team_1_score += connections_dict[tup[0]][1]
    
    team_2_score = 0
    for tup in groups_dict[2]:
        team_2_score += connections_dict[tup[0]][1]
    
    winner = ""
    if team_1_score > team_2_score:
        winner = "Group 1 wins!"
    elif team_2_score > team_1_score:
        winner = "Group 2 wins!"
    else:
        winner = "Its a tie"
    
    game_summary = "Game over!\n"
    game_summary += "Group 1 typed in {} characters.\nGroup 2 typed in {} characters.\n".format(team_1_score,team_2_score)
    game_summary += winner+"\n\n"

    if winner != "Its a tie":
        game_summary += "Congratulations to the winners:\n==\n"
        if winner == "Group 1 wins!":
            winners_names = get_teams_name(1)
        else:
            winners_names = get_teams_name(2)
        game_summary += winners_names
    
    # print(game_summary)
    connections_key_list = list(connections_dict.keys())
    lost_counter = 0
    while len(connections_key_list) > 0:
        try:
            connections_key_list[0].sendall(game_summary.encode("utf-8"))
            connections_key_list.pop(0)
            lost_counter = 0
        except:
            lost_counter += 1
            if lost_counter == 3: # trying to send the message 3 times
                print("lost connection with " + str(connections_dict[connections_key_list[0]][0][0]) +"\n")
                connections_key_list.pop(0)
                lost_counter = 0
            

    # for conn in connections_dict.keys():
    #     try:
    #         conn.sendall(game_summary.encode("utf-8"))
    #     except:
    #         pass
        


def player_listener(conn, stop_event):
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
    connections_dict[conn][1] = score



def send_udp():
    server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = struct.pack('Ibh', 0xfeedbeef, 0x2, TCP_PORT)
    server_socket_udp.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
    end_time = time.time() + 10
    while  time.time() < end_time:
        try:
            server_socket_udp.sendto(message,('<broadcast>', UDP_PORT))
            time.sleep(1)
        except:
            continue
    server_socket_udp.close()

def run_tcp_socket():
    end_time = time.time() + 10
    server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server started, listening on IP address "+str(IP_ADDRESS))
    while True:
        try:
            server_socket_tcp.bind(('',TCP_PORT))
            break
        except:
            continue
    
    server_socket_tcp.settimeout(2) # to remove
    server_socket_tcp.listen(4)

    groups_dict ={1:[],2:[]}
    connections_dict = {}
    while True:
        try:
            # try:
            #     connection_socket, client_address = server_socket_tcp.accept()
            # except:
            #     if time.time() >= end_time:
            #         raise
            #     continue
            connection_socket, client_address = server_socket_tcp.accept()
            team_name = connection_socket.recv(BUFFER_SIZE)
            connections_dict[connection_socket] = [client_address,0]
            team_name = team_name.decode("utf-8")[:-1]
            random_casting_to_group(connection_socket, team_name)
        except:
            if time.time() < end_time:
                continue
            message_to_send = message_builder()
            for conn in connections_dict.keys():
                connections_key_list = list(connections_dict.keys())
                lost_counter = 0
                while len(connections_key_list) > 0:
                    try:
                        connections_key_list[0].sendall(message_to_send.encode("utf-8"))
                        connections_key_list.pop(0)
                        lost_counter = 0
                    except:
                        lost_counter += 1
                        if lost_counter == 3: # trying to send the message 3 times
                            print("lost connection with " + str(connections_dict[connections_key_list[0]][0][0]) +"\n")
                            connections_key_list.pop(0)
                            lost_counter = 0
            play_the_game()
            server_socket_tcp.close()
            print("\nGame over, sending out offer requests...\n")
            break


while True:    
    udp_thread = Thread(target=send_udp)
    tcp_thread = Thread(target=run_tcp_socket)
    udp_thread.start()
    tcp_thread.start()
    udp_thread.join()
    tcp_thread.join()