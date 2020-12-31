import socket
import struct
from threading import Thread
import threading
import time
import random
from scapy.arch import get_if_addr

class server:
    """
    server class for the Keyboard Spamming Battle Royale.
    """
    def __init__(self, eth_num):
        """
        :param eth_num: 1 for development and 2 for testing.
        building a server object. 
        """
        self.MAGIC_COOKIE = 0xfeedbeef
        self.MESSAGE_TYPE = 0x2
        self.UDP_PORT = 13107
        self.TCP_PORT = 13118
        self.BUFFER_SIZE = 1024 
        self.GAME_ON = False  # True if the game started and else false
        self.CONNECTIONS_DICT = {}
        if eth_num == 1:
            self.IP_ADDRESS = get_if_addr("eth1")
        else:
            self.IP_ADDRESS = get_if_addr("eth2")
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.random_group_num = 0 # classify the client team to groups 1/2 randomly. 
        self.server_socket_udp.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        self.server_socket_tcp.bind((self.IP_ADDRESS,self.TCP_PORT))
        self.BROADCAST_IP = '172.1.255.255'
        self.GAME_DURATION = 10
        

    def run_udp(self):
        """
        method to send offers every second in udp.
        """
        end_time = time.time() + 10
        broadcast_message = struct.pack('Ibh', self.MAGIC_COOKIE, self.MESSAGE_TYPE, self.TCP_PORT)
        while time.time() < end_time:
            self.server_socket_udp.sendto(broadcast_message,(self.BROADCAST_IP, self.UDP_PORT))
            time.sleep(1)
        self.GAME_ON = True


    def run_tcp(self):
        """
        method to deal with tcp.
        this method will do the connections with the client via tcp
        and assign the clients to groups.
        at the end, the game is starting and clients get a message that the game started.
        """
        self.random_group_num = random.randint(1,2)
        print("Server started, listening on IP address "+str(self.IP_ADDRESS))
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
                       

    def run_the_game(self):
        """
        main game method.
        listen to all clients in different threads.
        calculate the score for each group and send the summary message.
        """
        self.run_all_listeners()
        self.send_game_over_message()
        team_1_score, team_2_score = self.calculate_score()
        game_summary_message = self.game_summary_builder(team_1_score, team_2_score)
        self.send_summary_message_to_players(game_summary_message)


    def send_game_over_message(self):
        """
        sends a message to all the clients that the game over.
        """
        for conn in self.CONNECTIONS_DICT.keys():
            conn.sendall("Game Over".encode("utf-8"))


    def calculate_score(self):
        """
        collect the score from each team and sum them by groups.
        """
        team_1_score = 0
        team_2_score = 0
        for conn_lst in self.CONNECTIONS_DICT.values():
            if conn_lst[1] == 1:
                team_1_score += conn_lst[2] 
            else:
                team_2_score += conn_lst[2]
        return team_1_score, team_2_score


    def game_summary_builder(self, team_1_score, team_2_score):
        """
        build the message that will be print on client screen.
        """
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
        """
        send the summary message to all clients. 
        :param summary_message: string of message
        """
        for conn in self.CONNECTIONS_DICT.keys():
            conn.sendall(summary_message.encode("utf-8"))


    def run_all_listeners(self):
        """
        make the server multi threaded that will listen to each client separately
        """
        list_of_players_threads = []
        list_of_stop_event = []
        for conn in self.CONNECTIONS_DICT.keys():
            stop_event = threading.Event()
            list_of_stop_event.append(stop_event)
            player_listen_thread = Thread(target=self.listen_to_player,args=(conn, stop_event, ))
            list_of_players_threads.append(player_listen_thread)
        # start all threads together (as possible) to avoid time differances.
        for thread in list_of_players_threads:
            thread.start() 

        time.sleep(self.GAME_DURATION)
        for stop_event in list_of_stop_event:
            stop_event.set()
        for thread in list_of_players_threads:
            thread.join()



    def listen_to_player(self, conn, stop_event):
        """
        method that listen to the client and counts pressing
        :param conn: the connection of the client
        :param stop_event: event that will stop the thread
        """
        score = 0
        while not stop_event.is_set():
            try:
                conn.settimeout(2)
                conn.recv(self.BUFFER_SIZE)
                if stop_event.is_set():
                    break
                score += 1
            except:
                if stop_event.is_set():
                    break
        self.CONNECTIONS_DICT[conn][2] = score
          

    def random_casting_to_group(self, connection_socket, team_name, group_num):
        """
        
        :param connection_socket: the connection of the client
        :param team_name: client team name
        :param group_num: team number for client
        """
        score = 0
        self.CONNECTIONS_DICT[connection_socket] = [team_name, group_num, score]
    

    def message_builder(self):
        """
        build the message that the client will recieve and will ynderstand that the game is on.
        """
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
        """
        reset the server and the necessary attributes
        """
        for sock in self.CONNECTIONS_DICT.keys():
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        self.CONNECTIONS_DICT = {}
        self.random_group_num = 0
        self.GAME_ON = False


    def run_server(self):
        """
        main method of the server. splited to 2 threads, one for udp and one for tcp.
        at the end of each loop, the server reset.
        """
        while True:
            udp_thread = Thread(target=self.run_udp)
            tcp_thread = Thread(target=self.run_tcp)
            udp_thread.start()
            tcp_thread.start()
            udp_thread.join()
            tcp_thread.join()
            time.sleep(3)
            self.reset_server()


if __name__ == "__main__":
    eth_num = 1
    server = server(eth_num)
    server.run_server()
