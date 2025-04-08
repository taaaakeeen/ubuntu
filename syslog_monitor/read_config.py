import configparser


def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


if __name__ == '__main__':

    config = read_config('syslog_monitor/syslog_receiver.conf')
    LOG_FILE = config.get('log', 'LOG_FILE')
    WHEN = config.get('log', 'WHEN')
    INTERVAL = int(config.get('log', 'INTERVAL'))
    BACKUP_COUNT = int(config.get('log', 'BACKUP_COUNT'))
    print([LOG_FILE, WHEN, INTERVAL, BACKUP_COUNT])
