from choice import choose
import time
import socket


class Connection:
    def __init__(self, data_received_callback, port):
        self.is_server = False
        self.my_name = ""
        self.their_name = ""
        self.port = port
        self.data_received_callback = data_received_callback
        self.buffer = bytearray()

    def send(self, data):
        data = data.encode("utf-8")
        length = len(data).to_bytes(2, byteorder="big")
        self.connection_sock.sendall(length + data)

    def poll(self):
        try:
            data = self.connection_sock.recv(4096)
            self.__handle_data(data)
        except BlockingIOError:
            pass
        except KeyboardInterrupt:
            self.connection_sock.close()

    def __handle_data(self, data):
        # TODO: if data == b"" => Handle disconnections
        self.buffer.extend(data)
        packet_length_known = False
        if len(self.buffer) >= 2:
            packet_length = int.from_bytes(self.buffer[:2], byteorder="big")
            packet_length_known = True

        while packet_length_known and packet_length <= len(self.buffer):
            packet = self.buffer[2:2+packet_length].decode("utf-8")
            self.data_received_callback(packet)
            self.buffer = self.buffer[2+packet_length:]

            if len(self.buffer) >= 2:
                packet_length = int.from_bytes(self.buffer[:2], byteorder="big")
            else:
                packet_length_known = False

    def close(self):
        self.connection_sock.close()


class Client(Connection):
    def __init__(self, username, data_received_callback, port):
        super().__init__(data_received_callback, port)
        self.is_server = False
        self.username = username
        
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.bind(("0.0.0.0", self.port))
        self.udp_sock.setblocking(False)

        self.connection_sock = None

        self.choose_server()

    def choose_server(self):
        time.sleep(0.1)
        while True:
            servers = self.list_servers()
            names = ["Join '" + server["username"] + "'" for server in servers]
            if len(servers) == 0:
                print("No server found. Your options:")
            else:
                print(f"{len(servers)} server found! Your options:")
            choice = choose(names, {"q": "Quit", "r": "Refresh"})
            if choice == "q":
                self.udp_sock.close()
                print()
                print("Goodbye!")
                exit()
            if choice == "r":
                print()
                continue

            success = self.connect(servers[choice]["ip"])
            if success:
                self.send(self.username)
                self.their_name = servers[choice]['username']
                print(f"Connected to {self.their_name}!")
                print()
                break
            else:
                print(f"{servers[choice]['username']} refused the connection :(")
                continue

    def get_next_server(self):
        try:
            data, addr = self.udp_sock.recvfrom(1024)
            return {"username": data.decode("utf-8"), "ip": addr[0]}
        except BlockingIOError:
            return

    def list_servers(self):
        servers = []
        server = self.get_next_server()
        while not server == None and not server in servers:
            servers.append(server)
            server = self.get_next_server()
        return servers

    def connect(self, ip):
        try:
            self.connection_sock = socket.socket()
            self.connection_sock.connect((ip, self.port))
            self.connection_sock.setblocking(False)
        except ConnectionRefusedError:
            return False
        self.udp_sock.close()
        return True
        

class Server(Connection):
    def __init__(self, username, data_received_callback, port):
        super().__init__(data_received_callback, port)
        self.is_server = True
        self.real_data_received_callback = data_received_callback
        self.data_received_callback = self.name_received_callback

        self.username = username
        
        try:
            self.server_sock = socket.socket()
            self.server_sock.bind(("0.0.0.0", self.port))
            self.server_sock.listen(5)
            self.server_sock.setblocking(False)
        except OSError:
            print("Failed to host game.")
            print("Aren't you already running a server on this machine?")
            self.server_sock.close()
            exit()
        
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.connected = False
        self.know_name = False
        self.connection_sock = None

        self.start()

    def start(self):
        print("Hosting game.")
        print("Waiting for connections...")
        while not self.connected:
            self.broadcast()
            self.accept_connection()
            time.sleep(1/10)
        while not self.know_name:
            self.poll()
            time.sleep(1/10)
    
    def accept_connection(self):
        try:
            conn, addr = self.server_sock.accept()
            conn.setblocking(False)
            self.connection_sock = conn
            self.udp_sock.close()
            self.server_sock.close()
            self.connected = True
        except BlockingIOError:
            pass

    def broadcast(self):
        self.udp_sock.sendto(bytes(self.username, "utf-8"), ("255.255.255.255", self.port))

    def name_received_callback(self, data):
        self.their_name = data
        print(f"Connected to {self.their_name}!")
        print()
        self.data_received_callback = self.real_data_received_callback
        self.know_name = True
        


def start(data_received_callback, port = 31313) -> Connection:
    name = input("Whats your name? ")
    print()
    print(f"Hello {name}!")
    print("What do you want to do?")
    answer = choose(["Host game", "Join game"], {"q": "Quit"})
    print()

    if answer == "q":
        print("Goodbye.")
        exit()
    elif answer == 0:
        return Server(name, data_received_callback, port)
    elif answer == 1:
        return Client(name, data_received_callback, port)