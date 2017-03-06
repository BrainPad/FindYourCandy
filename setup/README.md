Instruction
=====

## Space Requirement
- More than 50cm x 55cm ( recommend 80cmｘ80cm )  space required.
- See [requirements.md](./requirements.md) for layouts.


## Hardware Components
- Robot Arm
  - [Dobot Magician](http://dobot.cc/store/buy-dobot-magician.html)
  - Update to the latest firmware.
- Document camera
  - [Ipevo Ziggi-HD](https://www.amazon.com/dp/B01530XGMA)
  - [Ipevo Height Extension Stand](https://www.amazon.com/dp/B00CTIF2O0)
- [A3 marker sheet](./image/marker_paper.pdf)
  - for camera and robot arm to adjust their position
- Labeling tag
  - [Post-it 75 x 25mm](https://www.amazon.com/dp/B0013MW3PO/)
  - Yellow ones are easier to make good contrast with your pen color.
- Linux Box
  - [Intel NUC kit](https://www.amazon.com/dp/B01DG1SEES)
    - Core-i3 or i5 (included in Intel NUC kit)
    - HDMI or mini HDMI cable is needed accordingly.
  - 2 x [8GB Memory](https://www.amazon.com/dp/B00CQ35HBQ))
  - [SSD 250GB](https://www.amazon.com/dp/B0194MV5U8)（One of Sandisk’s long life (5 yrs) series is strongly recommended for price and stability. not samsung or other.）
- Tablet UI
  - Nexus9
    - Microphone (internal or external)
    - Chrome browser (to access linux box)
- See [requirements.md](./requirements.md) for the full list.



## Step1 : Place hardware components and Marker sheet
1. Print out [the marker sheet](./image/marker_paper.pdf) in A3 paper and stick it on the center
(This sheet will be used during both setup and demo.)
2. Build the robot arm by following manuals.
3. Place the robot arm to attach the A3 paper on A-D side.
4. Plugin the power supply unit of the robot arm to AC outlet.
5. Place the camera(CDVU-06IP) as shown below. In this case, camera should built with joint extender, CDVU-04IP-A1.
Note: Due to unavailability of 'CDVU-04IP-A1' in some regions including japan, a small box of 27-32cm in height can be used instead.

![](./image/arrangement.png)
![](./image/robot_and_camera.png)

## Step2 : Setup Linux box as controller PC.
1. Build your linux box by following direction of each manufacture.
  - You might need to mount ssd and memory inside the linux box unless they are already built in.
2. Connect both the robot arm and the camera to linux box.
  - The suction cup should be attached on arm end.
  - In some cases, we experienced the robot's firmware beeing outdated. In such a case, DobotStudio is required to upgrade its firmware(See manuals).
3. Connect the linux box to the internet using LAN cable.
4. During setup you need  a LCD display, a keyboard and a mouse. please prepare.
5. Install linux and softwares
  - Ubuntu 16.04.1 Server 64bit (You may also try Desktop 64bit, if your PC is well supported by Ubuntu.)
    - See [linux box.md](./linux_box.md)


#### Getting API credential.

This demo requires API credential for Google Cloud Platform(GCP). If this is your first project to use GCP, you can get an account from [cloud.google.com](https://cloud.google.com/).

1. Create a new GCP project
2. Enable the following APIs and services on [API Manager](https://support.google.com/cloud/answer/6158841)
  - Google Cloud Storage and Google Cloud Storage JSON API
  - Vision API
  - Speech API
  - Natural Language API
  - Cloud ML API
3. Create a service account key file
4. See [this doc](https://cloud.google.com/vision/docs/common/auth#set_up_a_service_account) to create a service account key
    - Service account: Compute Engine default service account
    - Key type: JSON
      - Save the JSON as /home/brainpad/FindYourCandy/credential.json
5. Set env variable
  - Add the following line (replace the path_to_your_own_credential_file with the actual JSON file path) to the last of `~/.bashrc` file.  

  ```
  export GOOGLE_APPLICATION_CREDENTIALS="path_to_your_own_credential_file"
  ```

6. Reopen the shell so that it takes effect

## Step3: Camera Calibation
The following instructions illustrates how to adjust the camera position.

1. Boot up linux box and login to the desktop.
2. Execute [(cd script ; python2 camera_tune.py)](./script/camera_tune.py) that is included in this demo software. And see the camera view in the window.
3. If you cannot see 'OK' sign in the window, tweak the camera or its extension and have whole image of A3 paper.
   - You may also try to get better focus by switching the AF slide between S and C on the camera.
   - In most cases, keeping the slide to S and pressing `[・] (focus)` button a few times does good in our environment.
4. You may click on left mouse button to exit this software.

![](./image/camera_calibration.png)

## Step4: Robot Arm Caribration
(* Read the safety manuals of your Robot Arm , befor proceeding this section.)


1. Start uwsgi-robot
  ```
  sudo systemctl stop  nginx.service # just make sure
  sudo systemctl start uwsgi-robot.service
  ```
2. Execute [(cd script ; python2 robot_tune.py)](./script/robot_tune.py) to start tuning the coordinates of arm.
3. Hit `Enter` key to initialize the robot arm.
4. Push the `release` button (which has symbol of `unlock` ) while you holding the robot arm by the other hand. Please be aware when the button is pressed, the robot arm looses friction and will start falling instantly. To avoid damaging your robot or desk, you should always assist robot arm when you press the `release` button.
5. Slowly land the arm edge to the center of `Maker A`. (still pressing the button.) Not on the letter 'A' but the target sign printed by the letter
6. Hit `Enter` key.
7. Repeat above 3,4 and 5 for Marker D and E.
8. The program saves those coordinates and ends automatically.
9. (You can see there are 3 lines of jsonl in `/tmp/robot_tuner.dat`.)
10. Restart to reload `/tmp/robot_tuner.dat`.
  ```
  sudo systemctl stop  nginx.service # just make sure
  sudo systemctl restart uwsgi-robot.service
  sudo systemctl start  nginx.service # finally nginx starts here
  ```

![](./image/robot_calibration.png)

## Step5: Tablet
1. Bootup Nexus9 and login with a google account for demo.
2. Update firmware.
3. Connect the [Ethernet Adapter for Chromecast](https://store.google.com/product/ethernet_adapter_for_chromecast)('GL0402') to Nexus9’s OTG connector. This is a hack to provide power and ether connection through USB cable when wifi is not proper to use.
4. Follow the “Set up Chromecast” on the [google support page](
https://support.google.com/chromecast/answer/2998456?hl=en)
\(there is instruction for Android 4.1 and higher\).
(* If you have a trouble with voice recognition of Nexus9, consider for external microphone.)

## Step6: Demo Application

#### Configure and run demo
  - See [README.md](../robot-arm) for robot-arm
  - See [README.md](../webapp) for webapp
