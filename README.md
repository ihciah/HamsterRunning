# Hamster Running

## Features:

- Log hamsters' wheel running to database

- Plot the data and send it to [Weibo](https://weibo.com/cangshucangshu) everyday

  ![Capture](Resources\Capture.JPG)



## Hardware:

- A raspberrypi

- A obstacle avoidance sensor (about 2RMB)

  

## How it works:

A sensor is used to detect the color of the wheel. Since the simplest obstacle avoidance sensor is driven by the light reflection, here draw the half of the wheel then it can be used to detect the color.

The raspberrypi reads the signal infinitely and write them to [influxdb](https://www.influxdata.com/). Every night the script reads the data, draws it and sends to weibo.



![Cage](Resources\Cage.jpg)

![Hardware](Resources\Hardware.jpg)

## Software Dependence:

- influxdb
- matplotlib
- requests_toolbelt
- numpy
- github.com/influxdata/influxdb/client/v2
- gobot.io/x/gobot

