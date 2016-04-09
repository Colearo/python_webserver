#!/usr/bin/env python3

import argparse

import sys
import itertools
import socket
import datetime
import threading
from socket import socket as Socket

# A simple web server

# Issues:
# Ignores CRLF requirement
# Header must be < 1024 bytes
# ...
# probabaly loads more

# Command line arguments. Use a port > 1024 by default so that we can run
# without sudo, for use as a real server you need to use port 80.
parser = argparse.ArgumentParser()
parser.add_argument('--port', '-p', default=9999, type=int,
                        help='Port to use')
args = parser.parse_args()

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

def main():

    # 相应网页的内容

    # Create the server socket (to handle tcp requests using ipv4), make sure
    # it is always closed by using with statement.
    with Socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # The socket stays connected even after this script ends. So in order
        # to allow the immediate reuse of the socket (so that we can kill and
        # re-run the server while debugging) we set the following option. This
        # is potentially dangerous in real code: in rare cases you may get junk
        # data arriving at the socket.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #设置连接及端口号
        server_socket.bind(('', args.port))
        server_socket.listen(10)

        print("服务器就绪，等待连接")
        
        while 1:
            #得到响应信息
            conn,addr = server_socket.accept()
            task = threading.Thread(target=soc,args=(conn,addr))
            task.start()
            
        server_socket.close()
            
    return 0
def soc(conn,addr):
    #打印出连接的客户端
    print('Connected with   '+addr[0] + 'Port on: ' + str(addr[1]))
    data = conn.recv(1024)
            #接受得到的数据
            
    tokens = data.split(b' ',1)
    command = tokens[0]
    if command == b'GET':
        http_response = 'HTTP/1.1 200 OK\r\nDate: Fri, 22 May 2009 06:07:21 GMT\nContent-Type: text/html; charset=UTF-8\r\n\r\n<h1>Hello, Httpserver!</h1>\n\t<h3>this is a test for httpserver by Python<h3><p>当前时间:<br>\n\t %s' % datetime.datetime.now().strftime(GMT_FORMAT)
        response = http_response.encode('UTF-8')
    else:
        response = b'HTTP/1.1 404 Not Found\r\n\r\n'
    conn.send(response)
    conn.close()
    print('Connection from %s : %s closed.' % addr)

if __name__ == "__main__":
    sys.exit(main())
