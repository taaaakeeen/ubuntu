import traceback
import os
from udp_receiver import UDPReceiver
from logger import RotatedLogger
from read_config import read_config


config = read_config('syslog_receiver.conf')
PORT = int(config.get('recv', 'PORT'))
BUFFER_SIZE = int(config.get('recv', 'BUFFER_SIZE'))
LOG_FILE = config.get('log', 'LOG_FILE')
WHEN = config.get('log', 'WHEN')
INTERVAL = int(config.get('log', 'INTERVAL'))
BACKUP_COUNT = int(config.get('log', 'BACKUP_COUNT'))


class SyslogReceiver(UDPReceiver):
    def __init__(self, host='0.0.0.0', port=PORT, buffer_size=BUFFER_SIZE):
        super().__init__(host, port, buffer_size)

        os.makedirs("log", exist_ok=True)

        self.app_logger = RotatedLogger(
            name='SyslogReceiver', 
            log_file=LOG_FILE, 
            console=True, 
            when=WHEN, 
            interval=INTERVAL, 
            backupCount=BACKUP_COUNT
        )

    def handle_message(self, data:bytes, addr):
        try:
            msg = f"[{addr[0]}] {data.decode('utf-8')}".rstrip("\n")
            self.app_logger.info(msg)
        except Exception as e:
            msg = f"{e}\n{traceback.format_exc()}".rstrip("\n")
            self.app_logger.error(msg)
        

if __name__ == '__main__':
    
    receiver = SyslogReceiver()
    try:
        receiver.start()
        input("Press Enter to end\n")
    finally:
        receiver.stop()
