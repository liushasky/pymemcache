import socketserver
import time
import threading
import pickle



class ThreadedTCPServer(socketserver.ThreadingMixIn,socketserver.TCPServer):    
    
    cache = {}

    def server_activate(self):
        """Called by constructor to activate the server.
        May be overridden.
        """
        path = '/Users/shaliu/Documents/Cloud Computing/storeddata.pickle'
        try:
            with open(path, 'rb') as f:
                print("load cache from {}".format(path))
                self.cache = pickle.load(f)
        except:
            self.cache = {}
        super().server_activate()

    def server_close(self):
        """
        override close function to pickle cache to disk.
        """
        super().server_close()
        path = '/Users/shaliu/Documents/Cloud Computing/storeddata.pickle'
        with open(path, 'wb') as f:
            print("dump cache to {}".format(path))
            pickle.dump(self.cache, f, protocol=pickle.HIGHEST_PROTOCOL)

class MyRequestHandler(socketserver.StreamRequestHandler):

    def handle(self):
        while True:
            cur_thread = threading.current_thread()
            print(cur_thread.name)

            if not self.rfile.peek():
                break
            data = self.rfile.readline().strip()
            print("{} wrote: {}".format(self.client_address[0], data))
            data_split = data.split()
            command = data_split[0].lower()
            if command == b"set":
                key, flags, exptime, length = data_split[1:5]
                no_reply = len(data_split) == 6

                value = self.rfile.read(int(length)+2)
                if exptime == b"0":
                    max_time = 0
                else:
                    max_time = time.time()+int(exptime)
                self.server.cache[key] = (int(flags), max_time, value[:-2])
                print(self.server.cache)
                if not no_reply:
                    self.wfile.write(b"STORED\r\n")
            elif command == b"get":
                key = data_split[1]
                output = b""
                
                if self.server.cache.get(key):
                    flags, max_time, value = self.server.cache[key]
                    if max_time > 0 and time.time() > max_time:
                        del self.server.cache[key]
                    else:
                        output += b"VALUE %s %d %d\r\n%s\r\n" % (key, flags, len(value), value)

                self.wfile.write(output + b"END\r\n")


    

