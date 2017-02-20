App setup
===

Prior to this instructions, make sure whole network is working good.
Here we quote ip address of Linux box as xxx.xxx.xxx.xxx.

### word2vec
```
$ mkdir -p ~/FindYourCandy/webapp/FindYourCandy/resources/models
# download word2vec model from https://github.com/mmihaltz/word2vec-GoogleNews-vectors to the 'models' directory
```


### Web appの起動
```
$ cd ~/FindYourCandy/webapp
$ export FLASK_ENV='stg'
$ python run.py
# access http://xxx.xxx.xxx.xxx:5000/predict
```
