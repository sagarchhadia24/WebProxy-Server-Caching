#****************************************************
#       Name:       Sagar Chhadia
#       UTA ID :    1001213987
#****************************************************

import socket
import threading
import logging
import os.path
from datetime import datetime
import time
import mimetypes

# Constant Variable
MAX_DATA_RECV = 999999


class HttpWebProxyServer(object):
    def __init__(self, host, port):
        self.cache_dir = "./cache/"
        self.log_dir = "./log/"

        # Write logs into file 'log.txt'
        logging.basicConfig(filename=self.log_dir + 'log.txt', format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
        #host = socket.gethostbyname(socket.gethostname())
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    # Method "listen" will listen for the client request on port "8888"
    def listen(self):
        self.sock.listen(1)
        print ('Web proxy running on "(%s, %d)"' % (self.host, self.port))
        logging.info('Web proxy running on "(%s, %d)"' % (self.host, self.port))
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            logging.info("Passing client: %s and address: %s" % (client, address))
            threading.Thread(target = self.listen_to_client,
                             args = (client,address)).start()

    # Method "parse_request" will parse the URL received from the client
    def parse_request(self, request):

        """
        To make request copy "http://localhost:8888/www.quora.com" in firefox browser

        Other URL List examples:
        1) http://localhost:8888/www.yahoo.com
        2) http://localhost:8888/www.zoomin.com
        3) http://localhost:8888/www.linkedin.com
        4) http://localhost:8888/www.gmail.com
        5) http://localhost:8888/www.icloud.com
        """

        logging.info("Request : %s" % (request));
        logging.info("Request Length: %d" % len(request));
        method = request.split(' ')[0]
        logging.info("method : %s" % (method));
        filename = request.split(' ')[1][1:]
        #print len(filename), filename
        logging.info("filename : %s" % (filename));
        return method, filename

    # Method "is_cached" will return is requested object is cached in the "cache_dir" or not
    def is_cached(self, filename):
        return os.path.isfile(self.cache_dir + filename)

    # Method "set_response_header" will set the response header based on the server response 
    def set_response_header(self, status_code, modified, length, mimetype):
        response_header = ''

        if status_code == 200:
            response_header += 'HTTP/1.1 200 OK\n'
            response_header += 'Server: HttpWebProxyServer\n'
            response_header += 'Last-Modified: ' + modified + '\n'
        elif status_code == 404:
            response_header += 'HTTP/1.1 404 Not Found\n'
            response_header += 'Server: HttpWebProxyServer\n'

        response_header += 'Content-Length: ' + str(length) + '\n'
        response_header += 'Content-Type: ' + mimetype + '\n'
        response_header += 'Connection: close\n\n'

        return response_header

    def get_mimetype(self, filename):
        try:
            (mimetype, encoding) = mimetypes.guess_type(filename, True)
            if not mimetype:
                return 'text/html'
            else:
                return mimetype
        except TypeError:
            return 'text/html'

    # Method "get_from_web_server" will get object from original server
    def get_from_web_server(self, client, method, filename):
        ##1.Get requested object from original server
        ##2.Cache this object
        ##3.Send requested object to client
        port = 80
        addr = filename.replace("www.","",1)
        logging.info('Connecting to webserver (%s, %d)' % (addr, port))
        try:
            # Create a socket to connect to the web server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((addr, int(port)))
            logging.info(b"GET " + b"http://" + filename.encode('utf-8') + b" HTTP/1.0\n\n")

            temp_file = sock.makefile('wrb', 0)
            temp_file.write(b"GET " + b"http://" + filename.encode('utf-8') + b" HTTP/1.0\n\n")
            buffer = temp_file.readlines()

            # Cache the requested object
            cache_file = open(self.cache_dir + filename, 'wb')
            for i in range(0, len(buffer)):
                cache_file.write(buffer[i])
                client.send(buffer[i])
                logging.info("Creating cache file\n")

            while True:
                # receive data from web server
                data = sock.recv(MAX_DATA_RECV)
                logging.info("Response Length: %s" % (data))
                if (len(data) > 0):
                    # send to browser
                    client.send(data)                        
                else:
                    break
        except Exception as e:
            response = "<html><body><p>Error 404: Not found</p></body></html>"
            #logging.info('Server Response: %s' % (response))
            response_header = self.set_response_header(404, '', len(response), 'text/html')
            #logging.info('Response Header:::: %s' % (response_header))
            client.send(response_header.encode() + response)
        finally:
            sock.close()
            client.close()

    # Method "listen_to_client" will listen request from client
    def listen_to_client(self, client, address):
        request = bytes.decode(client.recv(MAX_DATA_RECV))
        method, filename = self.parse_request(request)    

        if method == 'GET' :
            
            if self.is_cached(filename):
                ## Fie found in cache, send file to client
                try:
                    logging.info("Reading file from cache\n")
                    file_h = open(self.cache_dir + filename, 'rb')
                    response = file_h.read()
                    file_h.close()

                    modified = time.ctime(os.stat(self.cache_dir + filename)[8])

                    mimetype = self.get_mimetype(filename)

                    response_header = self.set_response_header(200, modified, len(response), mimetype)

                    client.send(response_header.encode() + response)
                except IOError:
                    logging.error('Cached file not found: %s' % filename)
                    self.get_from_web_server(client, method, filename)
                finally:
                    client.close()
                    
            else:
                # Cache file not available, Make request to original servver
                logging.info('Caching is not available for %s' % filename)
                self.get_from_web_server(client, method, filename)


if __name__ == "__main__":    
    HttpWebProxyServer('', 8080).listen()
