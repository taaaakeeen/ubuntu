import socket


class UDPSender:
    def __init__(self, host='127.0.0.1', port=10000, local_port=None, encoding='utf-8'):
        self.host = host # 送信先IP
        self.port = port # 送信先PORT
        self.encoding = encoding
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if local_port is not None:
            self.sock.bind(('0.0.0.0', local_port))

    def send(self, message: str):
        data = message.encode(self.encoding)
        self.sock.sendto(data, (self.host, self.port))

    def close(self):
        self.sock.close()


if __name__ == "__main__":

    sender = UDPSender(host='192.168.0.20', port=10000)
    sender.send("test message")
    sender.close()