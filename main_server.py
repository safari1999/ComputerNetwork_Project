from socket import *
import json

SERVER_PORT = 15000
CONNCTION_LIST = []
RESOURCES = list(range(10))
PEER_ID2ADDR = list(range(10))
for i in range(10):
    RESOURCES[i] = []
    PEER_ID2ADDR[i] = []


class Server:
    def __init__(self):
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('', SERVER_PORT))
        self.serverSocket.listen(5)
        self.peer_num = 0
        print('主服务器监听中...')

    def __del__(self):
        self.serverSocket.close()

    def handle_server(self):
        while True:
            connectionSocket, addr = self.serverSocket.accept()
            request_from_client = connectionSocket.recv(4096)
            print('客户端地址为', addr)
            print('客户请求:', request_from_client)
            request_from_client = request_from_client.decode()
            request_from_client = request_from_client.split(' ', 2)

            # 客户端注册
            if request_from_client[0] == '1':
                if addr[0] not in CONNCTION_LIST:
                    CONNCTION_LIST.append(addr[0])
                    self.peer_num = self.peer_num + 1
                    back_info = 'Register_successfully!_Your_id_is ' + str(self.peer_num)
                    connectionSocket.send(str.encode(back_info))
                    PEER_ID2ADDR[self.peer_num] = addr[0]
                else:
                    connectionSocket.send(str.encode("You have previously registered."))
            # update resources
            elif request_from_client[0] == '2':
                print('peer', addr[0], '更新了资源。')
                connectionSocket.send(str.encode('You are updating your resources'))
                client_id = connectionSocket.recv(4096)
                client_id = int(client_id.decode())
                connectionSocket.send(str.encode('I have known your id'))
                renew_str = connectionSocket.recv(4096)
                renew_str = renew_str.decode()
                renew = renew_str.split(";")
                print('id:', client_id)
                print('renew', renew)
                RESOURCES[client_id] = renew
                print(RESOURCES[client_id])

            # 下载文件
            elif request_from_client[0] == '3':
                peer_have_resource = []
                for i in range(10):
                    for data in RESOURCES[i]:
                        if data == request_from_client[1]:
                            peer_have_resource.append(PEER_ID2ADDR[i])
                if len(peer_have_resource) == 0:
                    peer_have_resource = ''
                else:
                    peer_have_resource = ";".join(peer_have_resource)
                connectionSocket.send(str.encode(peer_have_resource))
            # chatting with sb get peers online
            elif request_from_client[0] == '4':
                print('someone is getting online_peers:', CONNCTION_LIST)
                online_peers = ";".join(CONNCTION_LIST)
                connectionSocket.send(str.encode(online_peers))
            elif request_from_client[0] == '5':
                pass
            connectionSocket.close()

    # print('socket close')

    def ip2long(self, ip):
        iplist = ip.split(".")
        result = 0
        for i in range(4):
            result = result + int(iplist[i]) * 256 ** (3 - i)
        return result


if __name__ == '__main__':
    my_server = Server()
    my_server.handle_server()
    input()