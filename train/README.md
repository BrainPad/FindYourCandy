
### 画像から特徴量の抽出
```bash
python feature_extractor.py data/features \
--image_dir=data/images/test \
--model_dir=data/inception_model
```

image_dirは以下のような構造
```
image_dir
├── label_01
│   ├── image_01.jpg
│   └── image_02.jpg
├── label_02
│   ├── image_01.jpg
│   └── image_02.jpg
├── label_03
│   ├── image_01.jpg
│   └── image_02.jpg
└── label_04
    ├── image_01.jpg
    └── image_02.jpg
```


### 学習
```bash
gcloud beta ml local train \
--package-path=trainer \
--module-name=trainer.train \
-- \
--data_dir="/path/to/data/features" \
--train_dir="/path/to/train/test_train"'
```

model_dirは以下のinception v3のモデルデータを解凍したディレクトリを指定する
'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'

### 予測

```bash
python /ml/trainer/predict.py --data_dir=/ml/data/features  --train_dir=/path/to/train_dir'
```
train_dirにあるcheckpointからモデルをrestoreして予測する

```json
[
  {
    "url": "/path/to/images/image_0001.jpg",
    "top_lid": 0,
    "probs": [
      0.9989433884620667,
      0.0005387525307014585,
      7.3164969762729015e-06,
      0.000510607729665935
    ],
    "top_label": "label_0"
  },
  {
    ...
  },
  ...
]
```
