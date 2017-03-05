Requirements
===

### Layouts

![](./image/table_layout.png)
- Table Space: 50cm x 55cm (80cm x 80cm recommended)
  - Dobot: [physical Spec of Dobot](http://dobot.cc/dobot-magician/specification.html)
  - Document Reader: [physical Spec of Camera and Extension](https://www.amazon.com/dp/B01530XGMA)
  - Nexus 9: [physical Spec of Nexus 9](http://www.htc.com/us/tablets/nexus-9/)
  - A3: The marker sheet should be printed in good quality and sticked to the center of table.



### Robot hardware (about 2,500 USD per robot)
(When we demo there are 3 sets of these.)

- Robot arm : 1,159 USD
  - 1 x [Dobot Magician](http://dobot.cc/store/buy-dobot-magician.html) (Advance Education Plan)
    - Please update dobots by [DobotStudio](http://dobot.cc/download-center/dobot-magician.html)
    - (* If you have trouble updating its firmware, please find a driver for its serial chip [ch340/ch341](https://www.google.co.jp/search?q=ch340+windows10) and install.)
- Linux box: about 1,000 USD
  - 1 x [Intel NUC kit](https://www.amazon.com/dp/B01DG1SEES)
    - (This is where you install softwares.)
    - Core-i3 or i5 (included in Intel NUC kit)
    - HDMI or mini HDMI cable is needed accordingly.
    - Memory 16GB (2 x [Memory 8GB](https://www.amazon.com/dp/B00CQ35HBQ))
    - 1 x [SSD 128GB or more](https://www.amazon.com/dp/B0194MV5U8) (One of Sandisk's long life series is strongly recommended for price and stability. not samsung or other)
- Document Camera: 130 USD
  - 1 x [Ipevo Ziggi-HD Plus](https://www.amazon.com/dp/B01530XGMA)
  - 1 x [Extension stand](https://www.amazon.com/dp/B00CTIF2O0)
- Tablet UI
  - 1 x [Nexus 9 tablet](https://www.amazon.com/dp/B00M6UC5TG)
    - (Optional) Try this [external microphone](https://www.amazon.com/dp/B007517AKK) when you experienced poor voice recognition.
  - 1 x [Ethernet Adapter for Chromecast](https://store.google.com/product/ethernet_adapter_for_chromecast)
    - For connecting Nexus 9 to Ethernet
- Others
  - A few Ethernet cables.


### Lighting
- Environmental Lighting
  - Bright enough to detect markers.
  - No shadow over A3 paper.
- LED light (Optional)
  - Dimmerable LED light(s): [MOSPRO Cordless Clip Desk Lamp](https://www.amazon.com/dp/B0192XSVYM/) for an example, may be required to remove shadows on A3 paper.


### Networks
- Network connections
  - Internet access (to GCP, github, etc..)
  - DHCP server with DNS
  - IP reachability between linux box, Nexus9, and Chromecast
- 1 x Ethernet hub
  - 5 ports

### AC outlets
![](./image/networ_and_AC_outlet_layout.png)

- 4 x AC Outlets for each robot
 (if you have 3 robots, total is 12 outlets)
  - Robot Arm
  - Controller PC(linux box)
  - Ethernet adapter for Nexus 9
  - Ethernet hub
- (Additional) 3 x AC Outlets for making demo better.
  - HDMI Display (goes with Chromecast Ultra)
  - Ethernet Adapter for Chromecast (if you have trouble with wifi)
  - LED lighting (if you need)
