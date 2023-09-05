# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       arnaldoalicea                                                #
# 	Created:      9/5/2023, 4:10:45 PM                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()

frontleft = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
frontright = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
backleft = Motor(Ports.PORT3,GearSetting.RATIO_6_1,True)
backright = Motor(Ports.PORT4,GearSetting.RATIO_6_1,False)

player=Controller()

#--------end conf--------
def setup(value=0):
  if value == 1:
    pass #driver values
  else:
    pass #inital values de motores y whatnot
#--------driver Funcs---------
def joystickfunc():
  frontleft.spin(FORWARD)
  backleft.spin(FORWARD)
  frontright.spin(FORWARD)
  backright.spin(FORWARD)
  while True:
    frontleft.set_velocity(player.axis3.position()+player.axis1.position(),PERCENT)
    backleft.set_velocity(player.axis3.position()+player.axis1.position(),PERCENT)
    frontright.set_velocity(player.axis3.position()-player.axis1.position(),PERCENT)
    backright.set_velocity(player.axis3.position()-player.axis1.position(),PERCENT)
    wait(5,MSEC)

#--------auton funcs----------
def autonTime():
  pass #autonomo

#------comp funcs---------
def startDrivers():
  setup(1)
  driverTime.broadcast()

def autoF():
  active = Thread(autonTime)
  while (comp.is_autonomous() and comp.is_enabled()):
    wait(10,MSEC)
  active.stop()

def drivF():
  active = Thread(startDrivers)
  while (comp.is_driver_control() and comp.is_enabled()):
    wait(10,MSEC)
  active.stop()

driverTime = Event()
comp = Competition(drivF,autoF)
driverTime(joystickfunc)
wait(15,MSEC)

setup()