# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       arnaldoalicea                                                #
# 	Created:      9/5/2023, 4:10:45 PM                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #
# region --------conf--------
# Library imports
from vex import *
auton = 'offen' # selección de autonomo. defen/offen

# Brain should be defined by default
brain=Brain()

frontleft = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
frontright = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
backleft = Motor(Ports.PORT3,GearSetting.RATIO_6_1,True)
backright = Motor(Ports.PORT4,GearSetting.RATIO_6_1,False)
rightside = MotorGroup(frontright,backright)
leftside = MotorGroup(frontleft,backleft)
intake = Motor(Ports.PORT5,GearSetting.RATIO_18_1,True)
catapult1 = Motor(Ports.PORT6,GearSetting.RATIO_18_1,False)
catapult2 = Motor(Ports.PORT7,GearSetting.RATIO_18_1,True)
catapult = MotorGroup(catapult1, catapult2)
wings = DigitalOut(brain.three_wire_port.a)
wings2 = DigitalOut(brain.three_wire_port.b)
triballsens = Limit(brain.three_wire_port.c)

player=Controller()

def windup():
  catapult.set_stopping(HOLD)
  catapult.spin(FORWARD)
  while catapult.efficiency() > 50:
    wait(10,MSEC)
  catapult.stop()
def setup(value=0):
  if value == 1:
    rightside.set_velocity(50,PERCENT)
    leftside.set_velocity(50,PERCENT)
  else: 
    intake.set_velocity(100,PERCENT)#inital values de motores y whatnot
  wings.set(False)
  wings2.set(False)
# endregion
# region --------driver Funcs---------
def joystickfunc():
  leftside.spin(FORWARD)
  rightside.spin(FORWARD)
  while True:
    leftside.set_velocity(player.axis3.position()+player.axis1.position(),PERCENT)
    rightside.set_velocity(player.axis3.position()-player.axis1.position(),PERCENT)
    wait(5,MSEC)
def intakefunc():
  intake.set_velocity(100,PERCENT)
  while True:
    if player.buttonL2.pressing() and not triballsens.pressing():
      intake.spin(FORWARD)
    elif player.buttonL1.pressing():
      intake.spin(REVERSE)
    else:
      intake.stop()
def laCATAPULTA():
  catapult.set_velocity(100,PERCENT)
  catapult.set_stopping(COAST)
  while True:
    while player.buttonUp.pressing():
      catapult.spin(FORWARD)
      wait(5,MSEC)
    while player.buttonDown.pressing():
      catapult.spin(REVERSE)
      wait(5,MSEC)
    catapult.stop()
    wait(5,MSEC)
def wingManager():
  while True:
    if player.buttonR1.pressing():
      wings.set(True)
      wings2.set(True)
      while player.buttonR1.pressing():
        wait(10,MSEC)
      wings.set(False)
      wings2.set(False)
    wait(10,MSEC)
# endregion
# region --------auton funcs----------
def move(dis=float(24)):
  factor=5.5
  leftside.spin_for(FORWARD,dis/factor,TURNS,wait=False)
  rightside.spin_for(FORWARD,dis/factor,TURNS,wait=True)
  wait(5,MSEC)
def turn(theta=90):
  rightside.set_velocity(30,PERCENT)
  leftside.set_velocity(30,PERCENT)
  factor=48
  leftside.spin_for(FORWARD,theta/factor,TURNS,wait=False)
  rightside.spin_for(REVERSE,theta/factor,TURNS,wait=True)
  rightside.set_velocity(50,PERCENT)
  leftside.set_velocity(50,PERCENT)
  wait(5,MSEC)
def autonTime():
  setup(1)
  if auton == 'offen':
    intake.spin_for(FORWARD,1,TURNS,wait=False)
    move(49)
    turn(90)
    intake.spin_for(REVERSE,1.5,TURNS,wait=False)
    move(9.5)
    move(-18)
    turn(-90)
    intake.spin_for(FORWARD,1.5,TURNS,wait=False)
    move(5)
    move(-3)
    turn(85)
    intake.spin_for(REVERSE,2,TURNS,wait=False)
    move(21)
    move(-6)
    turn(86)
    move(50)
    turn(90)
    move(30)
  elif auton == 'defen':
    pass
# endregion 
# region ------comp funcs---------
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
# endregion
driverTime = Event()
comp = Competition(drivF,autoF)
driverTime(joystickfunc)
driverTime(intakefunc)
driverTime(wingManager)
driverTime(laCATAPULTA)
wait(15,MSEC)

setup()