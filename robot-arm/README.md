Copyright 2017 BrainPad Inc. All Rights Reserved.
robot-arm (api)
===

## Note
This software is design to work with Python2.7 under following condition.
- This software depends on the following libraries:
 - OpenCV3.2 (need to be compiled from source.)
  - Refer to [installation_instructions.md](../setup/installation_instructions.md) for installation.
 - Softwares you need to install from pip
 ```
  $ pip install -r requirements.txt
 ```
  ex)
  - Flask
  - uWSGI
  - numpy
  - pyserial

- Environment variables
    ```
    export FLASK_ENV='prd'   # choices are 'prd', 'stg' or 'dev'
    export PYTHONPATH=/usr/local/lib/python2.7/dist-packages
    ```

- Configuration files
  - web/config.py
    - DOBOT_SERVE_XY = (0, -150) # the destination of served candies.

- Network
  - TCP port 18001 need to be exposed to browser.

## Run
In this setup senario, this command is not used. We use nginx+uWSGI instead.
```
# Run app
$ python2 run_api.py  # Be sure python2.7 is selected
```

## API example
- POST /api/init
  - Initialize robot, and move to starting coordinates.
    - `curl -XPOST -d'{}' --header "Content-Type: application/json" localhost:18001/api/init`

- POST /api/pickup
  - Pick up a candy at given coordinates and serve it.
  - `curl -XPOST -d'{"x":150, "y":150}' --header "Content-Type: application/json" localhost:18001/api/status`

- GET /api/status
  - Get angles, coordinates, and the number of queued commands.
    - `curl -XGET --header "Content-Type: application/json" localhost:18001/api/status`
```sh
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
