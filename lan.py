import socket
import time


BUFSIZE = 4096
class Lan:
    def __init__(self, timeout):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(timeout)

    def open(self, IP, port):
        ret = False
        try:
            self.sock.connect((IP, port))
            ret = True
        except Exception as e:
            print("Error During open connection")
        return ret

    def close(self):
        ret = False
        try:
            self.sock.close()
            ret = True
            print("connection close")
        except Exception as e:
            print("Error During close connection")
        return ret

    def sendMsg(self, strMsg):
        ret = False
        try:
            strMsg = strMsg + '\r\n'                #Add a terminator, CR+LF, to transmitted command
            self.sock.send(bytes(strMsg, 'utf-8'))  #Convert to byte type and send
            ret = True
        except Exception as e:
            print(f"Error during send msg {e}")
        return ret

    def receiveMsg(self, timeout):
        msgBuf = bytes(range(0))  # Received Data
        try:
            start = time.time()  # Record time for timeout

            while True:
                rcv = self.sock.recv(BUFSIZE)
                # print("rvc : ", rcv)
                rcv = rcv.strip(b"\r")  # Delete CR in received data
                if b"\n" in rcv:  # End the loop when LF is received
                    rcv = rcv.strip(b"\n")  # Ignore the terminator CR

                    msgBuf = msgBuf + rcv
                    # print("without decode msgBuf : ", msgBuf)
                    msgBuf = msgBuf.decode('utf-8')
                    # print("msgBuf : ", msgBuf)
                    # print(type(msgBuf))
                    break
                else:
                    msgBuf = msgBuf + rcv
                    # print("msgBuf : ", msgBuf)
                # Timeout processing
                if time.time() - start > timeout:
                    msgBuf = "Timeout Error"
                    break
        except Exception as e:
            # print("Error during recive msg", e)
            msgBuf = f"Error {e}"
        return msgBuf

    def SendQueryMsg(self, strMsg, timeout):
        ret = Lan.sendMsg(self, strMsg)
        print("ret", ret)
        if ret:
            msgBuf_str = Lan.receiveMsg(self, timeout)  #Receive response when command transmission is succeeded
            #print("msg : ", msgBuf_str)
        else:
            msgBuf_str = "Error"

        return msgBuf_str