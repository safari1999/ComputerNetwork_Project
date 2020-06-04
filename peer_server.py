from socket import*
import os
import math
import threading

SERVER_ADDR = '192.168.199.102'
SERVER_PORT = 15000
PEER_PORT = 10086
MEGABYTE = 1024*1024
CHUNKSIZE = 10*MEGABYTE



class Peer:

	def __init__(self,peer_ip,peer_port):
		self.ip = peer_ip
		self.port = peer_port
		self.id = -1
		self.peer_socket = socket(AF_INET, SOCK_STREAM)
		self.peer_socket.bind(('',peer_port))
		self.peer_socket.listen(5)



	def __del__(self):

		self.peer_socket.close()

	#as a server

	def handle_download(self,connectionSocket,conaddr,filename,seq,total):

		filenum = self.split_file(filename)

		if filenum == None:

			return

		connectionSocket.send(str.encode(str(filenum)))
		connectionSocket.recv(4096)

		group_member = math.ceil(filenum/total)

		start_num = group_member*(seq-1)+1

		end_num = group_member*seq

		if end_num > filenum:

			end_num = filenum

		i = start_num

		while i <= end_num:

			new_file_name = filename+'_part_'+str(i)

			f = open(new_file_name,'rb')

			while True:

				content = f.read(4096)

				if content:

					connectionSocket.send(content)

				else:

					f.close()

					break
			i = i+1
			print(new_file_name,'sent successful')
	#as a server

	def handle_chat(self,connectionSocket,con_addr):
		print(con_addr,'连通中...')
		print(con_addr[0],'连通成功。（bye结束对话）')
		print('我:')
		my_response = input()

		connectionSocket.send(str.encode(my_response))
		print("等待回复...")
		other_greeting = connectionSocket.recv(4096)
		other_greeting = str(other_greeting.decode())
		print('peer:',other_greeting)
		while other_greeting != 'bye':

			my_response = input('我:')
			connectionSocket.send(str.encode(my_response))
			if my_response == 'bye':
				break
			print("等待回复中...")
			other_greeting = connectionSocket.recv(4096)
			other_greeting = str(other_greeting.decode())
			print('peer:',other_greeting)



	def handle_file_transport(self,connectionSocket,con_addr):

		pass

	#as a server

	def listening_to_others(self):
		print('监听中...')
		while True:

			connectionSocket, con_addr = self.peer_socket.accept()

			request_from_others = connectionSocket.recv(4096)

			request_from_others = str(request_from_others.decode())

			request_from_others = request_from_others.split(' ',4)
			print('request from others:',request_from_others)

			if request_from_others[0] == '1':
				print('==下载')
				filename = request_from_others[1]
				seq = request_from_others[2]
				seq = int(seq)
				total = request_from_others[4]
				total = int(total)
				self.handle_download(connectionSocket,con_addr,filename,seq,total)

			#chat with others

			elif request_from_others[0] == '2':
				print('==通信')

				self.handle_chat(connectionSocket,con_addr)

			elif request_from_others[0] == '3':

				self.handle_file_transport(connectionSocket,con_addr)

			connectionSocket.close()

	def split_file(self,filename):

		try:

			f = open(filename,'rb')

			f.close()

		except IOError:

			print('File is not accessible')

			return

		partnum = 0

		inputfile = open(filename,'rb')

		while True:

			chunk = inputfile.read(CHUNKSIZE)

			if not chunk:

				break

			partnum = partnum + 1

			file_split_name = filename+'_part_'+str(partnum)

			fileobj = open(file_split_name,'wb')

			fileobj.write(chunk)

			fileobj.close()

		return partnum

if __name__ == '__main__':
	print('请输入服务器地址：')
	SERVER_ADDR = input()
	print('请输入本地地址：')
	my_addr = input()
	my_peer = Peer(my_addr,PEER_PORT)
	my_peer.listening_to_others()
	input()