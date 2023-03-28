from socket import *
import threading
import sys
import json
import time
  
class Client:
    def __init__(self,name,server_ip,server_port,client_port):
        self.name = name
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind(('',self.client_port))
        self.is_connected = False #Used to check if the socket is connected or not
        self.client_table = []
        self.inGroup = False
        self.group_name = ""
        self.buffer = ""
        
    
    def connect(self):
        self.register()
        
        try:
            message = self.socket.recv(1024).decode()
            if message=="ack":
                self.is_connected =True
                print(">>>Successfully connect to server")
        
        except:
            print(">>> Failed to receive message from the server.")
            self.disconnect()
        
            
    def disconnect(self):
        if self.is_connected:
            self.socket.close()
            self.is_connected =False
            print(">>> Disconnected from the server")
            
    def register(self):
        msg = f"register\n {self.name}\n {self.client_port}\n "
        self.send(msg)
       
        
    def send(self,msg):
        
        self.socket.sendto(msg.encode(),(self.server_ip,server_port))
        
    
    def receive(self):
        while self.is_connected:
            try:
                ##look at the self buffer and print message:
                      
                
                buffer = self.socket.recv(1024).decode()
                buffer = buffer.split("\n")
                header = buffer[0]
                
                if header =="table": #if the header is table , decode the json
                    self.client_table  = json.loads(buffer[1])
                    print(self.client_table)
                    print(">>> Client table updated.")
                
                elif header=="private":
                    sender_name = buffer[1].strip()
                    sender_port = buffer[2]
                    msg = buffer[3]
                    
                    
                    for c in self.client_table:
                        if c['name'] == sender_name:
                            sender_address = tuple(c['address']) #must be tuple other wise it is a list
                    
                    ack_pack = f"{self.name} receive your message"
                    self.sendMessage("rcv_private",ack_pack,sender_address)
                    
                    message = f"{sender_name}: {msg}"
                    
                    #if in group mode, dont show the message
                    if self.inGroup:
                        self.buffer = message

                    
                    else:
                        print(message)
                        
                
                elif header =="rcv_private":
                    self.isPrivateMsgReceived =True
                
                elif header =="create_group":
                    self.isServerResponse = True
                    group_name = buffer[1].strip()
                    state = buffer[2].strip()
                    self.group_name =group_name
                    
                    if state =="created":
                        print(f">>>Group {group_name} created by server")
                    
                    else:
                        print(f">>>Group {group_name} already exists")
                
                elif header=="list_groups":
                    self.isServerResponse =True
                    group = buffer[1]
                    
                    print(group)
                
                elif header == "join_group":
                    self.isServerResponse =True
            
                    
                    state = buffer[1].strip()
                    
                    if state =="sucessfully":
                        print(">>>Entered group sucessfully")
                        self.inGroup =True
                    
                    else:
                        print(">>>Group does not exist")
                
                elif header == "send_group":
                    self.isServerResponse =True
                    print(">>>Message received by Server")
                
                elif header == "group_message":
                    group_name = buffer[1]
                    client_name = buffer[2].strip()
                    
                    message = ""
                    for i in range(3,len(buffer)):
                        message = message + buffer[i] + " "
                    
                    message = message.strip()     
                    print(f">>>{group_name} Group_Message {client_name}: {message}")
                    
                    #send a ack to server
                    header ="groupMessageReceived"
                    msg =""
                    self.sendMessage(header,msg,(self.server_ip,self.server_port))
                
                elif header =="list_members":
                    self.isServerResponse =True
                    memeber_name = buffer[1].strip()
                    group_name = self.group_name
                    print(f"({group_name}) {memeber_name}")
                
                elif header =="leave_group":
                    self.isServerResponse =True
                    self.inGroup = False
                    
                    
                   
                    
                    

                else:
                    print(buffer) 

            except Exception as e:
                print(e)
                print(">>> Failed to receive message from the server.")
                self.disconnect()
    
    
        
    def clientMessage(self):
        listen = threading.Thread(target=self.receive, args=()) #keep receiveing the message
        listen.start()
        
        while True:
            
        
            
            ##Normal mode:
            if self.inGroup == False:
                print(">>>", end="") #in client end, choose what to do, deregister, chat or create group
                temp = input()  # take inputs in the terminal
                input_list = temp.split()
                try:
                    header = input_list[0]
                except:
                    print("\n>>>Invalid input, try again dummy")
                    continue
            
                if header == "deregister": #deregister the socket
                    self.socket.sendto(f"deregister\n {self.name}\n {self.client_port}\n ".encode(),(self.server_ip,self.server_port))
                    print(">>>message sent")
                    
                
                elif header == "send": #send private message directly to other user
                    receiver_name = input_list[1]
                    message = ""
                    for i in range(2, len(input_list)):
                        message = message + input_list[i] + " " #pack the message after name
            
                    for c in self.client_table:
                        if c['name'] == receiver_name.strip():
                            receiver_address = tuple(c['address']) #must be tuple other wise it is a list
                            
                    self.sendMessage("private",message,receiver_address) #send a private message to
                    self.isPrivateMsgReceived = False
                    
                    time.sleep(0.5)
                    
                    if self.isPrivateMsgReceived:
                        print(f">>>Message received by {receiver_name}")
                    
                    else: #send a msg to server to update the status
                        header = "offline"
                        message = receiver_name
                        self.sendMessage(header,message,(self.server_ip,self.server_port))
                        print(f">>>No ACK from {receiver_name}, message not delivered")
                
                elif header =="create_group": # create a group
                    #have to check if in group or not: glaobal self.inGroup
                    
                    if self.inGroup ==False: 
                        group_name = input_list[1].strip()
                        header = "create_group"
                        msg = group_name
                        
                        self.sendMessage(header,msg,(self.server_ip,self.server_port)) #send the request to server
                        self.isServerResponse =False
                    
                    else:
                        print("You are already in group mode")
                    
                    time.sleep(0.5) #wait for 500ms to receive respond
                    if self.isServerResponse == False:
                        print(">>>Server not responding.")
                        print(">>>Existing") #if server does not respond
                
                elif header =="list_groups": #send command to server to list all group chats
                    header = "list_groups"
                    msg = ""
                    
                    self.sendMessage(header,msg,(self.server_ip,self.server_port))
                    self.isServerResponse = False
                    
                    time.sleep(0.5) #wait for 500ms 
                    
                    if self.isServerResponse == False:
                        print(">>>Server not responding.")
                        print(">>>Existing") #if server does not respond

                #join a group function
                elif header=="join_group":
                    group_name =input_list[1].strip()
                    header = "join_group"
                    self.group_name = group_name
                    
                    self.sendMessage(header,group_name,(self.server_ip,server_port))
                    self.isServerResponse =False
            
                    
                    time.sleep(0.5)
                    
                    if self.isServerResponse == False:
                        print(">>>Server not responding.")
                        print(">>>Existing") #if server does not respond
            
            ######Group Chat mode
            else: 
            #group chat mode  
            #send_group <group name> msg
                print(f">>> ({self.group_name}) ", end="") #in client end, choose what to do, deregister, chat or create group
                temp = input()  # take inputs in the terminal
                input_list = temp.split()
                try:
                    header = input_list[0]
                except:
                    print("\n>>>Invalid input, try again dummy")
                    continue
                
                if header == "deregister": #deregister the socket
                    self.socket.sendto(f"deregister\n {self.name}\n {self.client_port}\n ".encode(),(self.server_ip,self.server_port))
                    print(">>>message sent")
                          
                elif header =="send_group":
                    group_name = self.group_name
                    message = ""
                    for i in range(1, len(input_list)):
                        message = message + input_list[i] + " "
                    
                    #send the pck to the 
                    header = "send_group"
                    msg = f"{group_name}\n {message}"
                    
                    self.sendMessage(header,msg,(self.server_ip,self.server_port))
                    self.isServerResponse = False
                    
                    time.sleep(0.5)
                    if self.isServerResponse == False:
                        print(">>>Server not responding.")
                        print(">>>Existing") #if server does not respond
                
                elif header == "list_members":
                    header = "list_members"
                    msg =self.group_name
                    
                    self.sendMessage(header,msg,(self.server_ip,self.server_port))
                    self.isServerResponse = False
                    
                    time.sleep(0.5)
                    if self.isServerResponse == False:
                        print(">>>Server not responding.")
                        print(">>>Existing") #if server does not respond
                
                elif header == "leave_group":
                    header = "list_members"
                    group_name=self.group_name
                    msg = group_name
                    group_name = self.group_name
                    self.isServerResponse =False
                    
                    for i in range(5): #try 5 times to contact server
                        self.sendMessage(header,msg,(self.server_ip,self.server_port))
                        
                        time.sleep(0.5)
                        if self.isServerResponse:
                            break
                        
                        
                    if self.isServerResponse:
                        print(f">>> Leave group chat {group_name}")
                        print(self.buffer)
                        self.inGroup =False
        
                    
                    else:
                        self.inGroup =False
                        print(">>>Server not responding.")
                        print(">>>Existing") #if server does not respond
                    
                
                    
                    
                
                    
    
    def sendMessage(self,header,message,receiver_address):
        packet = f"{header}\n {self.name}\n {self.client_port}\n {message}".encode()
        
        self.socket.sendto(packet,receiver_address)
        print(">>>message sent")
    
   
            
            
            
        
class Server:
    def __init__(self,port_num):
        self.server_port = port_num 
        self.server_socket = socket(AF_INET,SOCK_DGRAM)   #create a udp socket
        
        #bind the socket to the server address and port
        self.server_socket.bind(('',self.server_port))
        
        #create clients table
        self.clients = []
        
        #create the groups list
        self.group_list = []
        
        
    def listen_to_user(self):
        
        print('Server is running on {}'.format(self.server_port))
        
        while True:
    
            buffer, client_address = self.server_socket.recvfrom(4096) #client address includes add + port 
            print("the client address is", client_address)

            buffer = buffer.decode() # always need to encode/decode messages
            lines = buffer.splitlines()
            header = lines[0]
            client_name = lines[1].strip()
            client_port = int(lines[2])
            msg = lines[3]
            print("The header is:", header)
            print(">>>" + msg)
            
            if header =="register": #if input is register from user
    
                self.clients.append({'name': client_name, 'address': tuple(client_address), 'port': client_port, 'status':"Yes"})
                
                print(self.clients)
                
                msg = "ack"
                self.server_socket.sendto(msg.encode(),(client_address))
                
                msg = "Welcome, You are registed!"
                self.server_socket.sendto(msg.encode(),(client_address))
                
                self.sendTable()
            
            elif header =="deregister": #if input is deregister from user
                for c in self.clients:
                    if c['name'] == client_name:
                        c['status'] = "No"
                
                de_msg = "Your are Offline. Bye!"
                self.sendTable()
                self.server_socket.sendto(de_msg.encode(),client_address)
                print(self.clients)
            
            elif header =="offline": #receive offline info and change the status of client
                offline_clinet = msg.strip() #offline clinet name
                
                for c in self.clients:
                    if c['name'] == offline_clinet:
                        c['status'] = "No"
                self.sendTable()

            elif header =="create_group":
                group_name = msg.strip()
                
                if group_name not in self.clients[0]: #check if the table has the group named by group name
                    for c in self.clients: #update the table
                        c[group_name] = "No"
                        self.sendTable()
                    
                    print(f"Client {client_name} created group {group_name} sucessfully")
                    
                    self.group_list.append(group_name) #add the group to the list
                    
                    #send ack back to clients:
                    header = "create_group"
                    msg = f"{group_name}\n created "

                    self.sendMessage(header,msg,client_address)
                
                else:
                    print(f"Client {client_name} created group {group_name} failed, group already exists")
                    header = "create_group"
                    msg = f"{group_name}\n exists"
                    self.sendMessage(header,msg,client_address)
            
            elif header =="list_groups":
                header = "list_groups"
                msg = self.group_list
                
                self.sendMessage(header,msg,client_address)

            elif header =="join_group":
                group_name =msg.strip()
                
                if group_name in self.clients[0]: #if the group exists
                    for c in self.clients:
                        if c['name'] == client_name:
                            c[group_name] = "Yes" #update the table
                            
                            #send a ack to client
                            header = "join_group"
                            msg = "sucessfully"
                            self.sendMessage(header,msg,client_address)
                            print(f"Client {client_name} joined group {group_name}")
                            
                        
                
                else: #if the group does not exist
                    header = "join_group"
                    msg = "notExist"
                    self.sendMessage(header,msg,client_address)
                    print(f"Client {client_name} joined group {group_name} failed, group does not exist")

            elif header =="send_group":
                
                group_name = lines[3].strip()
                
                message = ""
                for i in range(4,len(lines)):
                    message = message + lines[i] + " "
                
                print(f"Client {client_name} sent group message: {message}")
                
                
                #send a Ack to sender
                header = "send_group"
                msg = ""
                self.sendMessage(header,msg,client_address)
                
                #send a message to other clients in the group
                for c in self.clients:
                    if c['name'] != client_name:
                        if c[group_name] == "Yes": #if the status is yes
                            #send a message
                            header = "group_message"
                            msg =f"{group_name}\n {client_name}\n {message}"
                            
                            self.sendMessage(header,msg,c['address']) #send a group message
                            self.isClientRespond = False
                            
                            time.sleep(0.5)# wait for ack
                            
                            #after send a msg wait for  client
                            if self.isClientRespond ==False:
                                unRespond_client = c['name']
                                print(f">>>{unRespond_client} not responsive, removed from group {group_name}")
                                self.removeClientFromGroup(unRespond_client,group_name)
                                print(self.clients)

        
            elif header=="groupMessageReceived": #receive ack from client
                self.isClientRespond = True
            
            elif header=="list_members":
                group_name = msg.strip()
                header = "list_members"
                print(">>> {group_name} [Members in the group {group_name}:] ")
                for c in self.clients: #find the group
                    if c[group_name] == "Yes":
                        client_name = c['name']
                        print(f">>> ({group_name}) {client_name}")
                        self.sendMessage(header,client_name,client_address)

            elif header == "leave_group":
                group_name =msg.strip()
                print(f">>>Client {client_name} left group {group_name}")
                self.sendMessage(header,"",client_address)
                
                for c in self.clients:
                    if c['name'] == client_name:
                        c[group_name] = "No"
                
                print(self.clients)
                self.sendTable()
                
                
                        
                        
                
                
            
    def removeClientFromGroup(self,name,group_name):
        for c in self.clients:
            if c['name'] == name:
                c[group_name] = "No"
                        
    def sendMessage(self,header,msg,client_address):
        packet = f"{header}\n {msg}\n".encode()
        
        self.server_socket.sendto(packet,client_address)
        
        
                    
                
    
    def sendTable(self):   
        for c in self.clients:  #send table to every client
            if c['status'] == "Yes":
                c_socket = socket(AF_INET,SOCK_DGRAM)
                client_address = c['address']
                json_data = json.dumps(self.clients) #json list
                headers = "table\n"
                packet = headers.encode()+ json_data.encode()
                c_socket.sendto(packet,client_address)
                c_socket.close()
            
            
         

        

def serverMode(port):
    server = Server(port) #create server object
    server.listen_to_user() #server is listening to clients
    
    

        

def clientMode(user_name, server_ip, server_port, client_port):
    
    client = Client(user_name,server_ip,server_port,client_port)     
    client.connect() #connect to server if fails exit
    client.clientMessage()
    
    
        
        
      
        
if __name__ == "__main__":
    mode = sys.argv[1] #the command line, argv[0] is the name of script, [1] is the one after
    
    if mode =='-s': #In server mode
        s_port = int(sys.argv[2]) #port number from command line
        serverMode(s_port)
    
    elif mode =='-c':  #client mode
        user_name = sys.argv[2]
        server_ip = sys.argv[3]
        server_port = int(sys.argv[4])
        client_port = int(sys.argv[5])
        
        clientMode(user_name,server_ip,server_port,client_port)
    
    