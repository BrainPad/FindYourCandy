Copyright 2017 BrainPad Inc. All Rights Reserved.
webapp
===

## Note
This software is design to work with Python2.7 under following condtion.
- This software depends on the following libraries:
 - OpenCV3.2 (need to be compiled from source.)
  - Refer to installation_instructions.md for installation.
 - Softwares you need to install from pip
  ```
  $ pip install -r requirements.txt
  ```
  ex)
    - TensorFlow
    - Flask
    - uWSGI
    - google-cloud
    - scipy
    - gemsim

- Environment variables
    ```
    export FLASK_ENV='prd'   # choices are 'prd', 'stg' or 'dev'
    export GOOGLE_APPLICATION_CREDENTIALS="path_to_your_own_credential_file"
    export PYTHONPATH=/usr/local/lib/python2.7/dist-packages
    ```

- word2vec
  - download word2vec model from https://github.com/mmihaltz/word2vec-GoogleNews-vectors
  - copy it to the 'models' directory
  ```
  $ mkdir -p ~/FindYourCandy/webapp/candysorter/resources/models
  ```

- inception-V3
  - download inception-v3 model from http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz
  - copy it to the 'models' directory
  ```
  $ mkdir -p ~/FindYourCandy/webapp/candysorter/resources/models
  $ cd ~/FindYourCandy/webapp/candysorter/resources/models
  $ tar xvzf inception-2015-12-05.tgz classify_image_graph_def.pb
  ```

- Configuration files
  - candysorter/config.py
    - WORD2VEC_MODEL_FILE="path_to_GoogleNews-vectors-negative300.bin.gz"
     default path:
       candysorter/resources/models/GoogleNews-vectors-negative300.bin.gz
  - candysorter/config.py

- Network
  - TCP port 18000 need to be exposed to browser.

## Run app
After tuning the camera, you can start webapp.
```
$ sudo systemctl start uwsgi-webapp.service
```
In this setup senario, the next command is not used. We use nginx+uWSGI instead.
```
# Run app. This requres environment variables.
$ python2 run.py  # Be sure to use python2.7
```

## UI
Chrome web browser
- http://localhost:18000/predict


## API example
Morphological Analysis

```sh
$ curl -i -H "Content-type: application/json" -X POST http://localhost:18000/api/morphs \
    -d '{"text": "I like chewy chocolate candy", "id": "test"}'
```

Similarities

```sh
$ curl -i -H "Content-type: application/json" -X POST http://localhost:18000/api/similarities \
    -d '{"text": "I like chewy chocolate candy", "id": "testid"}'
```
