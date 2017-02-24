Trouble shooting
====


You may encounter some troubles, since we put our enphasis on making this demo simple and low cost.

### Camera troubles
- 'no device' message appears when executing camera_tune.py.
  It is likely to happen after you re-attach usb devices, because linux generates device files everytime you plug in usb devices or reboot whole system.
  1. Change the permision of device file.
     ```
     sudo chmod 777 /dev/video0
     ```
- The 'OK' sign does not appears on the screen.
  'camera_tune.py' cannot not control focus nor exposure of camera.
  1. Turn the robot arm to the opposite, so that the camera won't see it.
  1. Run 'camera_tune.py'
  1. (See how the focus is working on the screen.
     You should see 4 markers on each corner of A3 sheet.)
  1. If it's not well focused, push the focus button, right next to the slide switch located on top.
  1. Wait until focus is fixed.(takes about 2-3 seconds.)
  1. If the 'OK' sign does not appears, try exposure buttons to make picture brighter or dimmer.


### Robot troubles
- 'no device' message appears when executing robot_tune.py.
  It is likely to happen after you re-attach usb devices, because linux generates device files everytime you plug in usb devices or reboot whole system.
  1. Change the permision of device file.
     ```
     sudo chmod 777 /dev/ttyUSB0
     ```

- How do I reset the robot when it is bumpy?
  This may happen, when you hit the robot arm during its operation.
  1. Update the dobot firmware.
     (You need DobotStudio from [dobot.cc](http://dobot.cc/download.html) )
  1. Turn off the power switch of dobot.
  1. Unplug the USB cable.
  1. Unplug the power cable.
  1. Plug the USB cable again.
  1. Plug the power cable again.
  1. Change the permision of device file.
     ```
     sudo chmod 777 /dev/ttyUSB0
     ```
  1. Run the robot_tune.py.
  1. Restart the robot-arm's uWSGI to reload fixed cordinates.
     ```
     sudo systemctl start uwsgi-robot.service
     ```


### Demo is not working
- Error on browser 504
  1. Just wait wait for 3 minutes.(It takes a little while until all the data is loaded at begining .)
  1. If it is still not working and cpu is not busy, just restart.
     ```
     sudo systemctl restart uwsgi-robot.service
     ```


- Error on browser 502
  uWSGI is not working.
  1. sudo systemctl start uwsgi-webapp.service
