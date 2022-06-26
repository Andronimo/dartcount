import socket, queue

def openServer(q, port):
    TCP_IP = '127.0.0.1'
    TCP_PORT = port
    BUFFER_SIZE = 1024 

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    while 1:
        conn, addr = s.accept()
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        text = str(data, 'utf-8').rstrip("\n")
        q.put(text)
        #conn.send("--> {}\n".format(text).encode('utf-8'))  # echo
        conn.close()
