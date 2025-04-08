import os
import traceback
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler


class Logger(logging.Logger):
    def __init__(self, name, log_file, level=logging.INFO, console=False):
        super().__init__(name)

        formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.addHandler(console_handler)

        self.addHandler(file_handler)
        self.setLevel(level)


class RotatedLogger(logging.Logger):
    def __init__(self, name, log_file, level=logging.INFO, console=False, when='midnight', interval=1, backupCount=30, maxBytes=None):
        """
        :param name: ロガーの名前
        :param log_file: ログファイルのパス
        :param level: ログレベル (デフォルトは INFO)
        :param console: コンソールに出力するかどうか (デフォルトは False)
        :param when: ローテーションの周期 ('S', 'M', 'H', 'D', 'W0'-'W6', 'midnight', 'interval')
        :param interval: ローテーションの間隔
        :param backupCount: バックアップの保持数
        :param maxBytes: ログファイルの最大サイズ (バイト単位)
        """
        super().__init__(name)

        formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # ローテーション用のハンドラを作成
        if maxBytes:
            # ログサイズでローテーションする場合
            file_handler = RotatingFileHandler(log_file, maxBytes=maxBytes, backupCount=backupCount, encoding='utf-8')
        else:
            # 時間でローテーションする場合
            file_handler = TimedRotatingFileHandler(log_file, when=when, interval=interval, backupCount=backupCount, encoding='utf-8')

        file_handler.setFormatter(formatter)
        file_handler.rotator = self._custom_rotator
        
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.addHandler(console_handler)

        self.addHandler(file_handler)
        self.setLevel(level)

    def _custom_rotator(self, src:str, dst:str):
        # ファイル名に .log を追加
        if not dst.endswith('.log'):
            dst += '.log'
        os.rename(src, dst)


def test_logger():
    logger = Logger('Application', 'app.log', level=logging.DEBUG, console=True)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


def test_rotated_logger():
    logger = RotatedLogger(
        name='Application',
        log_file='app.log',
        level=logging.DEBUG,        # ログレベルを DEBUG に設定
        console=True,               # コンソールにも出力
        when='midnight',                   # 毎日ローテーション
        interval=1,                 # インターバル（1日）
        backupCount=7,              # 7日分のバックアップを保持
        # maxBytes=1024 * 1024 * 10   # 10MB でローテーション
    )
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


def test_error_log():
    try:
        s = 1 + ""
    except Exception as e:
        logger = Logger('Application', 'app.log', level=logging.DEBUG, console=True)
        msg = f"{e}\n{traceback.format_exc()}".rstrip("\n")
        logger.error(msg)


if __name__ == "__main__":

    # test_logger()
    # test_rotated_logger()
    test_error_log()
