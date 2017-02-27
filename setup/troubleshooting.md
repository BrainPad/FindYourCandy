Trouble shooting
====


You may encounter some troubles, since we put our enphasis on making this demo simple and low cost.

Camera troubles
---
##### 'No device' message appears when executing camera_tune.py.
- It is likely to happen after you re-attach usb devices, because linux generates device files everytime you plug in usb devices or reboot whole system.
1. Change the permision of device file.
 ```
 sudo chmod 777 /dev/video0
 ```
- The 'OK' sign does not appears on the screen.

##### 'camera_tune.py' cannot not control focus nor exposure of camera.
1. Turn the robot arm to the opposite, so that the camera won't see it.
2. Run 'camera_tune.py'
3. (See how the focus is working on the screen.
   You should see 4 markers on each corner of A3 sheet.)
4. If it's not well focused, push the focus button, right next to the slide switch located on top.
5. Wait until focus is fixed.(takes about 2-3 seconds.)
6. If the 'OK' sign does not appears, try exposure buttons to make picture brighter or dimmer.

##### Error message `Gtk-WARNING \*\*: cannot open display` on terminal

If you login to the linux box via ssh, this likely happens.
1. You first login to the desktop.
2. Then run 'camera_tune.py' after run.

Robot troubles
---
##### 'No device found' message appears when executing robot_tune.py.

- It is likely to happen after you re-attach usb devices, because linux generates device files everytime you plug in usb devices or reboot whole system.


1. Change the permision of device file.
   ```
   sudo chmod 777 /dev/ttyUSB0
   ```


##### How do I reset the robot when it is bumpy?
- This may happen, when you hit the robot arm during its operation.


1. Update the dobot firmware.
     (You need DobotStudio from [dobot.cc](http://dobot.cc/download.html) )
2. Turn off the power switch of dobot.
3. Unplug the USB cable.
4. Unplug the power cable.
5. Plug the USB cable again.
6. Plug the power cable again.
7. Change the permision of device file.
   ```
   sudo chmod 777 /dev/ttyUSB0
   ```
8. Run the robot_tune.py.
9. Restart the robot-arm's uWSGI to reload fixed cordinates.
   ```
   sudo systemctl start uwsgi-robot.service
   ```


Demo is not working
---
##### Error 504 on browser
- Until all models are loaded to webapp, all requests will be timed out with error 504 .
- The following is a list of all models loading during startup of webapp.
   - word2vec model (this is very large model and takes about 3 minutes to load.)
   - inception model
   - transfer model

   (* You can see the progress that has been made in webapp/log/app.log .)


1. Just wait for 3 minutes.(It takes a little while until all the data is loaded at begining .)
2. If it is still not working and cpu is not busy, just restart.
   ```
   sudo systemctl restart uwsgi-robot.service
   ```


##### Error 502 on browser
- uWSGI may be not working.


1. sudo systemctl start uwsgi-webapp.service
