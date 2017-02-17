### base setup
```
$ sudo chmod 777 /dev/ttyUSB0
$ sudo chmod 777 /dev/video0
$ cd ~
$ git clone git@github.com:BrainPad/CandySorter.git
$ cd ~/CandySorter
$ sudo pip install -r robot-arm/requirements.txt
$ sudo pip install -r webapp/requirements.txt
```

### word2vec
```
$ mkdir -p ~/CandySorter/webapp/candysorter/resources/models
# download word2vec model from https://github.com/mmihaltz/word2vec-GoogleNews-vectors to the 'models' directory
```

### GCP setup
```
# create your own project and credentials for API service.
# see also: (add links of each API's documentations)
$ export GOOGLE_APPLICATION_CREDENTIALS="path_to_your_own_credential_path"
```

### Web appの起動
```
$ cd ~/CandySorter/webapp
$ export FLASK_ENV='stg'
$ python run.py
# access http://localhost:5000/predict
```
