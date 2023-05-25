#!/usr/bin/env python3
from pupper_controller.src.pupperv2 import pupper
import math
from pupper_vision import vision
pup = pupper.Pupper(run_on_robot=True,
                        plane_tilt=0)  # -math.pi/8)
pup.slow_stand(do_sleep=True)
pup.start_trot()
def movetoPerson():
    while True:
        newdetect = open("detect_data.txt","r")
        detections = newdetect.readlines()
        # print(detections)
        centerdist = 0
        if detections:
            lastdetect = detections[max(len(detections)-2,0)]
            print(lastdetect[:-2])
       	    centerdist = float(lastdetect[:-2])
        #ob = pup.get_observation()
        current_turn_rate = 0 #currently just a p controller
        current_speed = 0 # currently just p control
        turn_rate = yawcontrol(0, current_turn_rate, centerdist)
        # speed = fwdcontrol(0, current_speed, depth)
        pup.step(action={"x_velocity": 0.08,
                        "y_velocity": 0.0,
                        "height": -0.14,
                        "yaw_rate": turn_rate,
                        "com_x_shift": 0.005})
def fwdcontrol(pos, vel, target):
    Kp = 0.003
    Kd = 0
    tau = Kp * (target - pos) + Kd * (-1*vel)
    return tau
    # control the rate of turn of pupper
def yawcontrol(pos, vel, target):
    #just p control for now
    Kp = 0.002
    Kd = 0
    tau = Kp * (target - pos) + Kd * (-1-vel)
    return tau
def main():
    print("hi")
    movetoPerson()
if __name__ == "__main__":
    main()
