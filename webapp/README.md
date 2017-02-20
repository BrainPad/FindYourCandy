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
  - download word2vec model from https://github.com/mmihaltz/word2vec-GoogleNews-vectors to the 'models' directory
  ```
  $ mkdir -p ~/FindYourCandy/webapp/candysorter/resources/models
  ```

- Configuration files
  - candysorter/config.py
    - WORD2VEC_MODEL_FILE="path_to_GoogleNews-vectors-negative300.bin.gz"
     default path:
       candysorter/resources/models/GoogleNews-vectors-negative300.bin.gz
  - candysorter/config.py

- Network
  - TCP port 18000 need to be exposed to browser.

## Run
In this setup senario, this command is not used. We use nginx+uWSGI instead.
```
# Run app
$ python2 run.py  # Be sure python2.7 is selected
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
$ curl -i -H "Content-type: application/json" -X POST http://localhost:5000/api/similarities \
    -d '{"text": "I like chewy chocolate candy", "id": "testid"}'
```
