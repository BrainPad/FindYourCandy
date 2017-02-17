Webアプリ
==============================

## 開発環境構築

### OpenCV

- 別途インストール
- 必要な場合は以下のようにライブラリのパスを設定
    ```sh
    $ echo "/path/to/opencv3/lib/python2.7/site-packages" >> /path/to/python/lib/python2.7/site-packages/opencv3.pth
    ```
    または、opencv3.2を PREFIX=/usr/local/でインストールしてある場合は、以下のように環境変数をいれておく。（virtualenv内でcv2.soをいれるのも面倒なので）
    ```
    export PYTHONPATH=/usr/local/lib/python2.7/dist-packages
    ```

### Pythonパッケージ

- TensorflowはOSによってダウンロード先が変わるので適宜変更
  virtualenv を実行している場合も、OSの生のPIPで以下のコマンドで
  tensorflowを入れておく必要があります。(tensorflow==0.12.1)
  ```
     sudo pip2 install -y
  ```
  ```sh
  $ pip install -r requirements/dev.txt
  ```

## 各種モデル取得

### Word2Vec

- Webから「GoogleNews-vectors-negative300.bin.gz」を取得
- candysorter/config.pyのWORD2VEC_MODEL_FILEで場所を指定
- **ファイルサイズが大きいのでリポジトリには入れない。**
    - 入れるならGit LFSを使う

    2017/2/12時点ではconfig.pyのパスは以下のように設定されています。
    例：webapp/candysorter/resources/models/GoogleNews-vectors-negative300.bin.gz
    ※ resources のディレクトリは含まれてないので作成します。


### Keras

- 簡易的に作成したものを以下に配置しているので適当に選んで取得
    - http://neumann:1289/edit/work/morooka/data/checkpoint/
- candysorter/config.pyのKERAS_MODEL_FILEで場所を指定

    2017/2/12時点ではconfig.pyのパスは以下のように設定されています。
    例：webapp/candysorter/resources/models/weights_20170208_195656.hdf5
    ※ resources のディレクトリは含まれてないので作成します。

- 動作確認用のダミーの画像データがリポジトリに含まれていないので、手動で追加します。

    2017/2/12時点では、webapp/candysorter/views/api.pyの中に次の様に ファイル名がハードコードされています。
    ```
    img = cv2.imread('./candysorter/resources/data/org/image_0001.png')
    ```


## GCPサービスアカウント取得

- GCPのサービスを使用しているので、どこかのプロジェクトでサービスアカウントを作成

```sh
$ export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```


## アプリケーションサーバ起動

- FlaskのデバッグモードだとTensorflowは動かない(かも)

```sh
# 環境指定
$ export FLASK_ENV='dev'
$ export FLASK_ENV='stg'
$ export FLASK_ENV='prd'

# アプリケーション起動
$ python run.py
```

## UI

- http://localhost:5000/perdict


## APIサンプル

### 形態素解析

```sh
$ curl -i -H "Content-type: application/json" -X POST http://localhost:5000/api/morphs \
    -d '{"text": "I like chewy chocolate candy", "id": "test"}'
```

### 類似度取得

```sh
$ curl -i -H "Content-type: application/json" -X POST http://localhost:5000/api/similarities \
    -d '{"text": "I like chewy chocolate candy", "id": "testid"}'
```
