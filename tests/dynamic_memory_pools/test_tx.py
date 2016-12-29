import socket
import threading
import argparse
from time import sleep

TCP_SOCKET_ARGS = socket.AF_INET, socket.SOCK_STREAM
UDP_SOCKET_ARGS = socket.AF_INET, socket.SOCK_DGRAM
NUMBER_OF_CONNECTIONS = 100
DATA_SIZE = 128  # (2**4) * (2**3) chars
DATA = '0123456789ABCDEF'* (2**3)

class DynamicMemHost:
    def __init__(self, *kwargs):
        self.server_ip = parsed_args.server_ip
        self.port = parsed_args.port
        self.transport = parsed_args.transport
        self.timeout = parsed_args.timeout
        self.socket_elem = None
    
    def run(self):
        if self.transport=='tcp': #(socket.AF_INET, socket.SOCK_STREAM)
            return self.run_tcp()
        else:
            return self.run_udp()

class ServerTX(DynamicMemHost):
    def __init__(self, *kwargs):
        DynamicMemHost.__init__(self, *kwargs)
        
        self.socket_elem = socket.socket(*(TCP_SOCKET_ARGS if self.transport == 'tcp' else UDP_SOCKET_ARGS))
        self.socket_elem.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_elem.bind((self.server_ip, self.port))
    
    def run_tcp(self):
        def listen_to_client(client, address):
            size = 1024
            while True:
                try:
                    data = client.recv(size)
                    if data:
                        # Set the response to echo back the recieved data
                        response = data
                        client.send(response)
                    else:
                        raise error('Client disconnected')
                except:
                    client.close()
                    return False

        self.socket_elem.listen(NUMBER_OF_CONNECTIONS*2)
        while True:
            ss, address = self.socket_elem.accept()
            ss.settimeout(60)
            td = threading.Thread(target = listen_to_client, args = (ss, address))
            td.start()


    def run_udp(self):
        pass


class ClientTX(DynamicMemHost):
    def __init__(self, *kwargs):
        DynamicMemHost.__init__(self, *kwargs)
        
    def run(self):
        if self.transport=='tcp':
            self.run_tcp()
        else:
            self.run_udp()
        
    def run_tcp(self): #
        step_iterations = 10
        step_connections = NUMBER_OF_CONNECTIONS/10
        client_sockets = []
        connect_error = 0
        
        for i in range(step_iterations):
            print("step:\t%d" % i)
            for j in range(step_connections): #open [step_connections] socket
                cs = socket.socket(socket.AF_INET)
                print len(client_sockets)
                while True:
                    try:
                        cs.connect((self.server_ip, self.port))
                        break
                    except:
                        sleep(1)
                        connect_error+=1
                        print (connect_error)
                        continue
                    
                client_sockets.append(cs)
                sleep(0.1)
            
            for cs in client_sockets:
                cs.send(DATA)
            
            for cs in client_sockets:
                recieved_data = cs.recv(DATA_SIZE)
                print recieved_data
                if (len(recieved_data) != DATA_SIZE or recieved_data != DATA):
                    print("ERROR: data returned corrupted.")
                    return -1
            
            sleep(1)
        
        for cs in client_sockets:
            cs.close()
                
            
        return 0
        
    def run_udp(self):
        pass
        
        

if __name__ == "__main__":
    EPILOG = """
    
"""
    
    parser = argparse.ArgumentParser(epilog=EPILOG)
    parser.add_argument('-host', dest="host", type=str,
                        choices=["server", "client"], default=None,
                        help="server or client")
    parser.add_argument('-trans', dest="transport", type=str,
                        choices=["tcp", "udp"], default="tcp",
                        help="tcp or udp")
    parser.add_argument('-ip', dest="server_ip", type=str, default='', #default: localhost
                        help="server ip")
    parser.add_argument('-port', dest="port", type=int, default=None,
                        help="port")
    parser.add_argument('-timeout', dest="timeout", type=str, default=None,
                        help="timeout")
    
    
    parsed_args = parser.parse_args()

    host = None
    if parsed_args.host == 'server':
        host = ServerTX(*vars(parsed_args))
    else:
        host = ClientTX(*vars(parsed_args))
        
    exit(host.run())
    
    