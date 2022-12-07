from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import logging
from concurrent.futures import ThreadPoolExecutor
import datetime

class ChatServer:
	def __init__(self, host, port):
		self.logger = self._setup_logger()
		self.sock = self._setup_socket(host, port)
		self.connections = []
	
	def run(self):
		self.logger.info("Chat server is running")
		with ThreadPoolExecutor() as executor:
			while True:
				# block and wait for incoming connections
				# returns a tuple containing a new socket object
				# with the connection and address of the client on the other end
				conn, addr = self.sock.accept()
				self.logger.debug(f"New connection: {addr}")
				self.connections.append(conn)
				self.logger.debug(f"Connections list: {self.connections}")
				executor.submit(self.relay_messages, conn, addr)

	def relay_messages(self, conn, addr):
		while True:
			data = conn.recv(4096)
			name, message = data.decode('utf-8').split('\n')
			self.logger.debug(f"Name {name}, | Message {message}")
			for connection in self.connections:
				a = str(addr[0] + " | ").encode('utf-8')
				now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
				now+=" | "
				now = now.encode('utf-8')
				self.logger.debug(f"Message from {name} : {message}")
				connection.send(a+ now + name + message)
			if not data:
				self.logger.warning("No data. Exiting")
				break

	@staticmethod
	def _setup_socket(host, port) :
		sock = socket(AF_INET, SOCK_STREAM)
		sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		sock.bind((host, port))
		sock.listen()
		return sock

	@staticmethod
	def _setup_logger():
		logger = logging.getLogger('chat server')
		logger.addHandler(logging.StreamHandler())
		logger.setLevel(logging.DEBUG)
		return logger

if __name__ == "__main__":
	from chat_docker.settings import SERVER_HOST, SERVER_PORT
	server = ChatServer(SERVER_HOST, SERVER_PORT)
	server.run()	