# dobot制御apiサーバ

dobotを接続した状態で `python run_api.py` で起動する

#### `POST /api/init`
`curl -XPOST -d'{}' --header "Content-Type: application/json" 172.16.1.74:8000/api/init`
dobotアームの座標初期化プロトコルを実行する

#### `POST /api/pickup` 
指定したxy座標のお菓子を拾って `DOBOT_SERVE_XY` のxy座標に落とす
`curl -XPOST -d'{"x":150, "y":150}' --header "Content-Type: application/json" 172.16.1.74:8000/api/status`

#### `GET /api/status`
dobotの各部位の角度、アーム先端の角度、内部コマンドキューに残っているコマンド数を取得する
`curl -XGET --header "Content-Type: application/json" 172.16.1.74:8000/api/status`
```
{
  "basement": 43.86176300048828, 
  "end": 0.0, 
  "fore": 68.0941162109375, 
  "queue_count": 0, 
  "r": 43.86176300048828, 
  "rear": 60.5015869140625, 
  "x": 124.26170349121094, 
  "y": 119.42009735107422, 
  "z": -69.91238403320312
}
```
