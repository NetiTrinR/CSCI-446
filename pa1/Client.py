import http.client as httplib, urllib.parse as ulib

class Client:
	def get_coor(self):
		coor = input("X Y: ")
		if coor == "exit":
			return
		coor = coor.split()
		if len(coor)<2:
			print("Missing Y co-ordinate.")
		else:
			try:
				# coor[0] = int(coor[0])
				# coor[1] = int(coor[1])
				self.send_post(coor)
			except ValueError:
				print("Please input numbers only.")
		self.get_coor()

	def send_post(self,coor):
		params = ulib.urlencode({'x':coor[0], 'y':coor[1]})
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
		conn = httplib.HTTPConnection("127.0.0.1", 5000)
		conn.request("POST", "", params, headers)
		response = conn.getresponse()
		print(str(response.status)+" "+response.reason)
		data = response.read().decode("utf-8")
		print(data)
		conn.close()
		
	def __init__(self):
		print("Welcome to CSCI 466 Battleship game!!");
		print("To fire (0,0) input \"0 0\" in console.");
		print("To exit the game, innput exit.\n");
		self.get_coor()

client = Client()
