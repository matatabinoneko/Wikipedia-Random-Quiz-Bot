# LINEBOT template
LINE botを開発するためのテンプレート

### 動かすためにやること
- LINE BOTを作成する
   - https://developers.line.biz/en/
- `backend/src/`ディレクトリに`token_key.py`を作成し，以下のコードを記入
    ```python
    YOUR_CHANNEL_ACCESS_TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN"
    YOUR_CHANNEL_SECRET = "YOUR_CHANNEL_ACCESS_TOKEN"
    ```
    トークンはそれぞれ書き換えてください
- ngrokとdockerをインストール
  - macなら`brew install ngrok --cask`とか？

### 起動の仕方
```bash
docker-compose build
docker-compose up -d
ngrok http 5000
```
### 停止の仕方
docker-compose down
