from socket import*
import os
import math

SERVER_PORT = 15000
PEER_PORT = 10086
MEGABYTE = 1024*1024
CHUNKSIZE = 10*MEGABYTE

class Peer_client:
	def __init__(self,peer_ip):
		self.ip = peer_ip
		self.id = -1
	def __del__(self):
		pass

	def register(self):
		print('===peer注册===')
		clientSocket = socket(AF_INET,SOCK_STREAM)

		clientSocket.connect((SERVER_ADDR,SERVER_PORT))

		peer_info = '1 '+str(self.ip)+' .'

		clientSocket.send(str.encode(peer_info))

		response_from_server = clientSocket.recv(4096)
		response_from_server = response_from_server.decode()
		response_from_server = response_from_server.split(' ',2)
		if self.id == -1:
			self.id = int(response_from_server[1])
		print(" ".join(response_from_server))
		print('id ：',self.id)
		clientSocket.close()

	def update_resource(self):

		path = os.getcwd()

		own_resource = os.listdir(path)

		clientSocket = socket(AF_INET,SOCK_STREAM)

		clientSocket.connect((SERVER_ADDR,SERVER_PORT))

		clientSocket.send(str.encode('2 update_resource'))

		response_from_server = clientSocket.recv(4096)

		print(response_from_server)
		clientSocket.send(str.encode(str(self.id)))
		clientSocket.recv(4096)
		print('本地资源',own_resource)
		own_resource = ";".join(own_resource)
		clientSocket.send(str.encode(own_resource))
		clientSocket.close()

	def chat_with_sb(self):

		online_peers = self.get_peers_online()
		print('在线:',online_peers)

		my_friend = input('选择peer通信(ipv4 address)')

		if my_friend in online_peers:

			clientSocket = socket(AF_INET,SOCK_STREAM)
			clientSocket.connect((my_friend,PEER_PORT))
			greeting = "2  I'm chatting with you! If one of us say 'bye',the chatting will end."
			clientSocket.send(str.encode(greeting))
			print("等待回复中...")
			friend_response = clientSocket.recv(4096)
			friend_response = str(friend_response.decode())
			print('peer',my_friend,":",friend_response)
			while friend_response != 'bye':
				greeting = input('我:')
				clientSocket.send(str.encode(greeting))
				if greeting == 'bye':
					break
				print("等待回复中...")
				friend_response = clientSocket.recv(4096)
				friend_response = str(friend_response.decode())
				print('peer:',my_friend,":",friend_response)

		else:
			print('输入peer不存在')

	def get_peers_online(self):
		clientSocket = socket(AF_INET,SOCK_STREAM)
		clientSocket.connect((SERVER_ADDR,SERVER_PORT))
		my_request = '4 get_peers_online'
		clientSocket.send(str.encode(my_request))
		online_peers = clientSocket.recv(4096)
		online_peers = online_peers.decode()
		online_peers = online_peers.split(";")

		clientSocket.close()

		return online_peers

	def download_resource(self):
		clientSocket = socket(AF_INET,SOCK_STREAM)
		clientSocket.connect((SERVER_ADDR,SERVER_PORT))
		print('===下载===')
		request_file = input('请输入请求文件名：')
		my_request = '3 '+request_file
		clientSocket.send(str.encode(my_request))
		peer_have_resource = clientSocket.recv(4096)
		peer_have_resource = peer_have_resource.decode()
		if len(peer_have_resource) == 0:
			pass
		else:
			peer_have_resource = peer_have_resource.split(";")
		print('peer_have_resource',peer_have_resource)
		clientSocket.close()

		if len(peer_have_resource) == 0:
			print('文件不存在。')

		else:
			if len(peer_have_resource) >= 2:
				filenum = self.download_helper(request_file,peer_have_resource[0],1,2)
				self.download_helper(request_file,peer_have_resource[1],2,2)
			else:
				filenum = self.download_helper(request_file,peer_have_resource[0],1,1)
			self.combine_file(request_file,filenum)
		self.update_resource()

	def download_helper(self, filename, dst_ip, seq, total):

		download_socket = socket(AF_INET, SOCK_STREAM)

		download_socket.connect((dst_ip, PEER_PORT))

		download_socket.send(str.encode('1 ' + filename + ' ' + str(seq) + ' of ' + str(total)))

		filenum = download_socket.recv(4096)
		filenum = filenum.decode()
		print('filenum', filenum, ' type:', type(filenum))
		filenum = int(filenum)
		download_socket.send(str.encode("ok"))
		group_member = math.ceil(filenum / total)

		start_num = group_member * (seq - 1) + 1

		end_num = group_member * seq

		if end_num > filenum:
			end_num = filenum

		i = start_num

		while i <= end_num:

			new_file_name = filename + '_part_' + str(i)

			f = open(new_file_name, 'wb+')

			while True:

				content = download_socket.recv(4096)

				if content:

					f.write(content)

				else:

					f.close()

					break
			i = i + 1
			print('file', new_file_name, 'write successful')

		download_socket.close()
		return filenum

	def sending_out_request(self):

		print('请选择服务')

		print('1.下载文件')

		print('2.peer通信')

		while True:

			print('请选择服务')

			act = input()

			if act == '1':
				self.download_resource()

			elif act == '2':

				self.chat_with_sb()

			elif act == '3':

				pass
			else:
				print('无效指令。')

	def combine_file(self,filename,filenum):

		outfile = open(filename,'wb')

		for i in range(filenum):

			file_split_name = filename+'_part_'+str(i+1)

			infile = open(file_split_name,'rb')

			data = infile.read()

			outfile.write(data)

			infile.close()

		outfile.close()

if __name__ == '__main__':
	print('请输入服务器地址：')
	SERVER_ADDR = input()
	print('请输入本地地址：')
	my_addr = input()
	my_peer = Peer_client(my_addr)
	print('peer',my_addr)
	my_peer.register()
	my_peer.update_resource()
	my_peer.sending_out_request()
	input()