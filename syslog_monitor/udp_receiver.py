import socket
import threading


class UDPReceiver:
    def __init__(self, host='0.0.0.0', port=10000, buffer_size=4096):
        self.host = host # 受信IP
        self.port = port # 受信PORT
        self.buffer_size = buffer_size
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self._thread = None

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._thread.start()

            msg = f"UDP受信開始: {self.host}:{self.port}"
            print(msg)

    def _receive_loop(self):
        try:
            while self.running:
                data, addr = self.sock.recvfrom(self.buffer_size)
                self.handle_message(data, addr)
        except Exception as e:
            msg =  f"ERROR: {e}"
            print(msg)
        finally:
            self.sock.close()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()

        msg = f"UDP受信停止: {self.host}:{self.port}"
        print(msg)

    def handle_message(self, data:bytes, addr):
        ip = addr[0]
        msg = f"[{ip}] {data.decode('utf-8')}"
        print(msg)


if __name__ == '__main__':

    receiver = UDPReceiver(port=10000)
    try:
        receiver.start()
        input("Press Enter to end\n")
    finally:
        receiver.stop()
