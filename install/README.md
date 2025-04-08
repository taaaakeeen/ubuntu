# ubuntuのインストール

## 1. イメージファイルのダウンロード
https://jp.ubuntu.com/download

## 2. ディスクのフォーマット

diskpartの起動
```
diskpart
```

フォーマットするディスクの確認
```
list disk
```

```
ディスク      状態           サイズ   空き   ダイナ GPT
###                                          ミック
------------  -------------  -------  -------  ---  ---
ディスク 0    オンライン           931 GB  1024 KB        *
ディスク 1    オンライン            14 GB      0 B        *
```

フォーマットするディスクの選択
```
select disk 1
detail disk
clean
create partition primary
list partition
```

フォーマットの実行
```
format fs=fat32 quick
```

## 3. Rufusのダウンロード
https://rufus.ie/ja/

## 4. Rufusでフラッシュメモリにイメージファイルを書き込む

<img src="data/images/2025-04-05 145704.png">

## SSHのインストール
```
sudo apt install openssh-server
```

サービス再起動
```
sudo systemctl restart ssh
sudo systemctl status ssh
```