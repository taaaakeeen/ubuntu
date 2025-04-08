# Ubuntuのsyslogを監視してUDPで外部へログを送信
<img src="data/images/2025-04-08 155300.png">

# 目次
1. PostgreSQLの設定
    - 1-1. 設定ファイルの編集
    - 1-2. 意図的にエラーを発生させる
    - 1-3. ログの確認
2. syslog監視スクリプトの作成
3. UDP受信プログラムの実行
4. syslog監視スクリプトの自動実行

# 1. PostgreSQLの設定

## 1-1. 設定ファイルの編集

PostgreSQLのインストール
```
sudo apt install postgresql postgresql-contrib
```

pg_hba.confの編集
```
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

```
# Allow replication connections from localhost, by a user with the
# replication privilege.
host    all             all             0.0.0.0/0            md5
```

postgresql.conf編集
```
sudo nano /etc/postgresql/14/main/postgresql.conf
```

```
# - Connection Settings -
listen_addresses = '*'

# - Where to Log -
log_destination = 'stderr,syslog'

# These are relevant when logging to syslog:
syslog_facility = 'LOCAL0'
syslog_ident = 'postgres'
```

サービス再起動
```
sudo systemctl restart postgresql
```

syslogの確認
```
tail -f /var/log/syslog | grep postgres
```

```
Apr  8 12:48:13 ubuntu-01 postgres[117400]: [9-1] 2025-04-08 12:48:13.919 JST [117400] postgres@test ERROR:  duplicate key value violates unique constraint "users_pkey"
Apr  8 12:48:13 ubuntu-01 postgres[117400]: [9-2] 2025-04-08 12:48:13.919 JST [117400] postgres@test DETAIL:  Key (user_id)=(satoshi) already exists.
Apr  8 12:48:13 ubuntu-01 postgres[117400]: [9-3] 2025-04-08 12:48:13.919 JST [117400] postgres@test STATEMENT:  INSERT INTO users (user_id, email)
```

## 1-2. 意図的にエラーを発生させる

DBサーバ接続
```
psql -h 192.168.0.44 -p 5432 -U postgres
```

DB作成
```
create database test;
```

DB接続
```
\c test
```

テーブル作成
```
CREATE TABLE users (
    user_id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

テストデータ挿入
```
INSERT INTO users (user_id, email)
VALUES ('satoshi', 'satoshi@example.com');
```

テストデータ確認 
```
SELECT * FROM users;
```

制約違反を発生
```
INSERT INTO users (user_id, email)
VALUES ('satoshi', 'satoshi@example.com');
```

存在しないテーブルを参照
```
SELECT * FROM not_exist_table;
```

存在しない列を参照
```
SELECT not_exist_column FROM test;
```

## 1-3. ログの確認

ログイン
```
sudo -i -u postgres
```

ログの確認
```
cd /var/lib/postgresql/14/main/log
ls
cat postgresql-2025-04-08_084308.log
```

```
2025-04-08 12:48:13.919 JST [117400] postgres@test ERROR:  duplicate key value violates unique constraint "users_pkey"
2025-04-08 12:48:13.919 JST [117400] postgres@test DETAIL:  Key (user_id)=(satoshi) already exists.
2025-04-08 12:48:13.919 JST [117400] postgres@test STATEMENT:  INSERT INTO users (user_id, email)
```

ログアウト
```
exit
```

# 2. syslog監視スクリプトの作成
```
sudo nano /usr/local/bin/monitor_postgresql_log.sh
```

```
#!/bin/bash

# ログ出力先ディレクトリをユーザーのホームに設定
# LOG_DIR="$HOME/monitor_postgres_log"
# mkdir -p "$LOG_DIR"

# syslogファイルの場所を判定（RedHat系: /var/log/messages, Ubuntu: /var/log/syslog）
if [ -f /var/log/syslog ]; then
    SYSLOG_FILE="/var/log/syslog"
elif [ -f /var/log/messages ]; then
    SYSLOG_FILE="/var/log/messages"
else
    echo "Syslog ファイルが見つかりません。終了します。"
    exit 1
fi

# tailでエラー行を監視してUDP送信＋ファイルに出力
tail -F "$SYSLOG_FILE" | grep --line-buffered "postgres" | grep --line-buffered "ERROR\|DETAIL\|STATEMENT" | while read line; do

    # logfile="$LOG_DIR/$(date '+%Y-%m-%d').log"

    log_entry="$line"

    # ファイルに追記
    # echo "$log_entry" >> "$logfile"

    # UDPでログを送信
    echo "$log_entry" | nc -u -w1 192.168.0.20 10000
done
```

スクリプトの実行
```
/usr/local/bin/monitor_postgresql_log.sh
```

# 3. UDP受信プログラムの実行

syslog_receiver.confを編集
```
[recv]
# PORT: 受信ポート
# BUFFER_SIZE: 受信データの最大サイズ
PORT = 10000
BUFFER_SIZE = 4096

[log]
# LOG_FILE: 出力するログファイル
# WHEN: ローテーションのタイミング
# INTERVAL: ローテーションの間隔
# BACKUP_COUNT: バックアップの保持数
LOG_FILE = log/syslog_receiver.log
WHEN = midnight
INTERVAL = 1
BACKUP_COUNT = 30
```

syslog_receiverの実行
```
python syslog_receiver.py
```

syslog_receiver.logの確認
```
2025-04-08 12:51:37.162 - SyslogReceiver - INFO - [192.168.0.44] Apr  8 12:48:13 ubuntu-01 postgres[117400]: [9-1] 2025-04-08 12:48:13.919 JST [117400] postgres@test ERROR:  duplicate key value violates unique constraint "users_pkey"
2025-04-08 12:51:38.162 - SyslogReceiver - INFO - [192.168.0.44] Apr  8 12:48:13 ubuntu-01 postgres[117400]: [9-2] 2025-04-08 12:48:13.919 JST [117400] postgres@test DETAIL:  Key (user_id)=(satoshi) already exists.
2025-04-08 12:51:39.166 - SyslogReceiver - INFO - [192.168.0.44] Apr  8 12:48:13 ubuntu-01 postgres[117400]: [9-3] 2025-04-08 12:48:13.919 JST [117400] postgres@test STATEMENT:  INSERT INTO users (user_id, email)
```

実行ファイルの作成
```
pyinstaller syslog_receiver.py --name syslog_receiver_v1.0.exe --onefile
```

# 4. ログ送信スクリプトの自動実行

スクリプトに実行権限を付与
```
sudo chmod +x /usr/local/bin/monitor_postgresql_log.sh
```

systemdサービスファイルを作成
```
sudo nano /etc/systemd/system/monitor_postgresql_log.service
```

```
[Unit]
Description=Monitor PostgreSQL log and forward errors
After=network.target syslog.target

[Service]
Type=simple
ExecStart=/usr/local/bin/monitor_postgresql_log.sh
User=ubuntu
Restart=always
WorkingDirectory=/home/ubuntu
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

サービスの有効化と起動
```
sudo systemctl daemon-reload
sudo systemctl enable monitor_postgresql_log.service
sudo systemctl start monitor_postgresql_log.service
```

サービスの状態確認
```
sudo systemctl status monitor_postgresql_log.service
```

再起動後にプロセス確認
```
ps aux | grep monitor_postgresql_log.sh
```

ログ確認
```
journalctl -u monitor_postgresql_log.service -f
```

停止
```
sudo systemctl stop monitor_postgresql_log.service
```

無効化
```
sudo systemctl disable monitor_postgresql_log.service
```
