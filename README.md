# Stanford Quadruped

## Overview
This repository hosts the code for Stanford Pupper and Stanford Woofer, Raspberry Pi-based quadruped robots that can trot, walk, and jump. 

![Pupper CC Max Morse](https://live.staticflickr.com/65535/49614690753_78edca83bc_4k.jpg)

Video of pupper in action: https://youtu.be/NIjodHA78UE

Project page: https://stanfordstudentrobotics.org/pupper

Documentation & build guide: https://pupper.readthedocs.io/en/latest/

## How it works
![Overview diagram](imgs/diagram1.jpg)
The main program is ```run_robot.py``` which is located in this directory. The robot code is run as a loop, with a joystick interface, a controller, and a hardware interface orchestrating the behavior. 

The joystick interface is responsible for reading joystick inputs from a UDP socket and converting them into a generic robot ```command``` type. A separate program, ```joystick.py```, publishes these UDP messages, and is responsible for reading inputs from the PS4 controller over bluetooth. The controller does the bulk of the work, switching between states (trot, walk, rest, etc) and generating servo position targets. A detailed model of the controller is shown below. The third component of the code, the hardware interface, converts the position targets from the controller into PWM duty cycles, which it then passes to a Python binding to ```pigpiod```, which then generates PWM signals in software and sends these signals to the motors attached to the Raspberry Pi.
![Controller diagram](imgs/diagram2.jpg)
This diagram shows a breakdown of the robot controller. Inside, you can see four primary components: a gait scheduler (also called gait controller), a stance controller, a swing controller, and an inverse kinematics model. 

The gait scheduler is responsible for planning which feet should be on the ground (stance) and which should be moving forward to the next step (swing) at any given time. In a trot for example, the diagonal pairs of legs move in sync and take turns between stance and swing. As shown in the diagram, the gait scheduler can be thought of as a conductor for each leg, switching it between stance and swing as time progresses. 

The stance controller controls the feet on the ground, and is actually quite simple. It looks at the desired robot velocity, and then generates a body-relative target velocity for these stance feet that is in the opposite direction as the desired velocity. It also incorporates turning, in which case it rotates the feet relative to the body in the opposite direction as the desired body rotation. 

The swing controller picks up the feet that just finished their stance phase, and brings them to their next touchdown location. The touchdown locations are selected so that the foot moves the same distance forward in swing as it does backwards in stance. For example, if in stance phase the feet move backwards at -0.4m/s (to achieve a body velocity of +0.4m/s) and the stance phase is 0.5 seconds long, then we know the feet will have moved backwards -0.20m. The swing controller will then move the feet forwards 0.20m to put the foot back in its starting place. You can imagine that if the swing controller only put the leg forward 0.15m, then every step the foot would lag more and more behind the body by -0.05m. 

Both the stance and swing controllers generate target positions for the feet in cartesian coordinates relative the body center of mass. It's convenient to work in cartesian coordinates for the stance and swing planning, but we now need to convert them to motor angles. This is done by using an inverse kinematics model, which maps between cartesian body coordinates and motor angles. These motor angles, also called joint angles, are then populated into the ```state``` variable and returned by the model. 


## How to Build Pupper
Main documentation: https://pupper.readthedocs.io/en/latest/

You can find the bill of materials, pre-made kit purchasing options, assembly instructions, software installation, etc at this website.


## Help
- Feel free to raise an issue (https://github.com/stanfordroboticsclub/StanfordQuadruped/issues/new/choose) or email me at nathankau [at] stanford [dot] edu
- We also have a Google group set up here: https://groups.google.com/forum/#!forum/stanford-quadrupeds


# Vision 
The vision stack is currently in initial stages of development. We are using an OAKD-Lite (Fixed Focus) to give Pupper eyes, complemented by DepthAI's python software package to run lean computer vision models for object detection and tracking. There are many opportunities to improve Pupper's vision stack, and here's how to start!

## Winter 2023 Final Project
During the Winter 2023 offering of CS199P, one team (Mark Leone and Ryan Dwyer) started the initial work for giving pupper a set of eyes (aka PupPerception). During the Winter 2023 quarter we:
- Initially wanted to have Pupper chase a ball. TinyYolo (which has ball as a class) drew too much power, and MobileNet was able to run onboard, so the task was changed to Pupper chasing a human.
- Debugged OAKD hardware issues (large power draw of OAKD-Lite while running models causes brownout, fixed this by powering RasPi and pupper actuators with separate power supplies)
- Received data from MobileNet using pupper_vision_2.py by identifying a person and taking the center of the bounding box around that person and writing it to a text file
- Used that CV data to autonomously command Pupper by running a PD control loop in pup_move.py that yaws pupper so that the center of Pupper's field of view is aligned with the center of the bounding box around the human
- By running pupper_vision_2.py and pup_move.py simultaneously in 2 terminals, Pupper can autonomously orient itself toward a person!

We created the directions below so that you can enable autonomy on your own Pupper using the OAKD-Lite!

## Install requirements
You need to download several software packages to run Pupper's computer vision stack properly. Each of them are described below. 

### StanfordQuadruped Repo
git clone this repo, and use "git checkout vision" to make sure you are cloned into this branch of the repository. 

### depthai-python
depthai-python contains the models, example code, and CV dependencies to process the data from the OAKD-Lite
- Follow the instructions on the depthai-python github (https://github.com/luxonis/depthai-python) to download depthai-python
- For your first time using DepthAI on any machine, run "install_requirements.py" within depthai-python/examples to get all dependencies
- Try running examples/ObjectTracking/object_tracker.py on your machine as a test to make sure all dependencies are met

### X11 forwarding -- IMPORTANT --
One problem you run into when running depthai-python code on Pupper's RasPi is that the RasPi does not have a monitor, and the code is designed to display the bounding boxes and CV data in real time on a monitor. To prevent from issues associated with this, you must enable X11 forwarding before SSHing into the RasPi onboard Pupper. This will display the real time Pupper vision on your machine's monitor rather than trying to display it on the RasPi. First, you must download an X11 forwarding program.

Mac: 
- Download XQuartz https://www.xquartz.org/
- Run XQuartz every time before SSHing into the RasPi (it may run without even popping up on your screen)
- SSH as normal but add "-X" to the end of your SSH command. For example: ssh pi@raspberrypi.local -X

Windows:
- Download XMing
- Run XMing very time before SSHing into the RasPi (it may run without even popping up on your screen)
- SSH as normal (with Putty https://www.putty.org/) but in Putty, click on the plus sign to the left of "SSH" in the left hand pane, then click "X11" and check the box labeled "Enable X11 Forwarding". You can save these settings in Putty.

## Python Version
Always run your commands on the RasPi with "python3" rather than "python" since DepthAI code is not compatible with Python 2.7, which is the default on the Pi.

## Hardware troubleshooting
- Use a USB3-USBC cable (the one with a blue inner piece) to connect the RasPi and the OAKD-Lite. Make sure this is plugged into one of the USB3 (blue inner piece) ports on the RasPi
- Unplug the jumper cables that power the RasPi from the onboard PCB. You don't want to power the RasPi from onboard and offboard power simultaneously
- Use an external USB-C cable to power the RasPi. This plugs into the top of Pupper

## Software troubleshooting
- Make sure to follow directions in the X11 forwarding section above. This is the root of most problems

## Current Work
Mark:
- Playing with a pupper depth control loop so that Pupper can follow a person accurately (hopefully done before ICRA)
- Using real multiprocessing rather than writing to .txt file for running vision and control loops separately

Spring 2023 Final Projects:
- Project 1: Obstacle avoidance and QR codes
- Project 2: Combining pupper vision and LLMs
- Project 3: Making pupper play soccer

## Help 
If you run into any problems, would like to collaborate, or have any questions, please email me at mleone [at] stanford [dot] edu