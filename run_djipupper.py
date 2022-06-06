# Usage
# python run_djipupper.py --run_on_robot

from pupper_controller.src.pupperv2 import pupper
from pupper_controller.src.interfaces import JoystickInterface
import math
import time
from absl import app
from absl import flags
flags.DEFINE_bool("run_on_robot", False,
                  "Whether to run on robot or in simulation.")
FLAGS = flags.FLAGS
def run_controller():
    pup = pupper.Pupper(run_on_robot=FLAGS.run_on_robot,
                        plane_tilt=0)  # -math.pi/8)
    pup.reset()
    if (FLAGS.run_on_robot):
        pup.hardware_interface.send_dict({"home": True})
    time.sleep(10)
    print("starting...")
    pup.slow_stand(do_sleep=True)
    pup.start_trot()

    joystick_interface = JoystickInterface.JoystickInterface(pup.config)
    try:
        while True:
            command = joystick_interface.get_command(pup.state)
            pup.step(action={"x_velocity": command.horizontal_velocity[0],
                             "y_velocity": command.horizontal_velocity[1],
                             "yaw_rate": command.yaw_rate,
                             "height": command.height,
                             "com_x_shift": 0.005})
            state = pup.get_observation()
            time.sleep(0.01)
    finally:
        pup.shutdown()
def main(_):
    run_controller()
if __name__=='__main__':
    app.run(main)