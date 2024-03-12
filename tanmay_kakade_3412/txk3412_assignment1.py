#!/usr/bin/env python3
'''
Name: Tanmay Kakade
UTAID: 1002023412
Python Version: 3.8

Main Reference: https://github.com/kiredroffas/Multithreaded-HTTP-Server/blob/master/MultiThreadedHttpServer.py
Threading reference: https://docs.python.org/3/library/threading.html
Socket Programming: https://realpython.com/python-sockets/#multi-connection-client-and-server
'''
import socket
import time
import threading
import signal
import sys

def client_threads(s):
   conn_client, address = s.accept()  
   print('Got connection from',address,'\n')
   # Create new thread to deal with client request, and continue accepting connections
   threading.Thread(target=client, args=(conn_client, address)).start()

#client data recieved and respond
def client(conn_client, address):
   persist_conn = False
   #While loop to keep listening active to exit clt + c twice
   while True:
      try:
         '''
         started recieving the client request with the browser data and
         different kind of data
         '''
         client_request = conn_client.recv(1024).decode()
         '''
         Closing not active connection. If not closed number of
         thread will be created and give index out of range
         '''
         if not client_request:
            print("Closing client connection as no active connection!!")
            conn_client.close()
            break
         #Extracting header related data from the recived request
         request_method = client_request.split(' ')[0]     
         http_version = client_request.split('/')[2][:3]
         print("Request Body: \n" + client_request)
         '''
         For http 1.1 persistent connection remain open till client closes
         but if header is not present we need to set timeout.
         Reference: https://serverfault.com/questions/731486/do-http-1-1-persistent-connections-timeout
         '''        
         if http_version == '1.1' and persist_conn == False:
            persist_conn = True
            conn_client.settimeout(10)
         #Responding to the client for GET http method request
         if request_method == "GET":
            '''
            From the client_request object we split to make it list &
            get the 2nd position which has file name after the localhost:port
            '''
            file_requested = client_request.split()[1]
            #To get the default or root index html file
            if file_requested == "/":
               file_requested = "/index.html"
            #file type at list postion 1
            try:
               #With loop to avoid using closing by explitly mentening it
               with open(file_requested.replace("/", ""), 'r') as html:
                 response_data = html.read()
               #Create header
               recived_header = header_response(200, http_version)
               '''
               Sending the content of the index.html to browser along with the header to 
               browser.
               '''
               print(recived_header)
               conn_client.send(recived_header.encode() + response_data.encode())
            except Exception as e:
               print("404 File Not Found!!!")
               recived_header = header_response(404, http_version)
               print(recived_header)
               conn_client.send(recived_header.encode())
         else:
            print("ERROR: Other than GET HTTP request method:  " + request_method)
            print("Stoping client socket...")
            conn_client.close()
            break
      # Exception is thrown once the socket connection times out (http 1.1 - persistent connection)
      except socket.timeout:
         print("Socket connection timeout reached (10 seconds), closing client socket...")
         conn_client.close()
         break
# Generates http response headers based on http protocol version and response code
def header_response(response_code, http_version):
   header = ''
   time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
   # If http version is 1.0, close connection after serving response
   if http_version == '1.0':  
      if response_code == 200:
         header += 'HTTP/1.0 200 OK\n'
      if response_code == 404:
         header += 'HTTP/1.0 404 Not Found\n'
      header += 'Date: ' + time_now + '\n'
      header += 'Server: Tanmay\'s Python Server\n'
      header += 'Connection: close\n'
   # If http version is 1.1, keep connection alive after serving response
   elif http_version == '1.1':  
      if response_code == 200:
         header += 'HTTP/1.1 200 OK\n'
      elif response_code == 404:
         header += 'HTTP/1.1 404 Not Found\n'
      header += 'Date: ' + time_now + '\n'
      header += 'Server: Tanmay\'s Python Server\n'
      #connection will keep alive
      header += 'Connection: keep-alive\n'
      header += 'Content-Type: text/html\n\n'
   return header

if __name__ == "__main__":
   '''
    Socket object is initialize with parameter
    socket.AF_INET which is the internet address 
    family for IPv4 and socket.SOCK_STREAM is
    the type for TCP for transfering stream over 
    netw
   '''
   try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
      print("Socket initiated")
      PORT=8085
      sock.bind(('localhost', PORT))
      print("Socket is binded for localhostd and "+ str(PORT) + "\n")
      # Have the socket listen for up to 5 connections
      sock.listen(4)
      print("Waiting for the connection....")
      while True:
         # Accept new connection from incoming client
         client_threads(sock)
   except KeyboardInterrupt:
      print("Keyboard interrupt")
   except Exception as e:
      print(e)
      sys.exit()