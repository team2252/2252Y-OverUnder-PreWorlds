# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       arnaldoalicea                                                #
# 	Created:      9/5/2023, 4:10:45 PM                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #
# region ------------conf-------------
# Library imports
from vex import *
auton = '' # selección de autonomo fisico :)

# Brain should be defined by default
brain=Brain()

frontleft = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
frontright = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
backleft = Motor(Ports.PORT3,GearSetting.RATIO_6_1,True)
backright = Motor(Ports.PORT4,GearSetting.RATIO_6_1,False)
rightside = MotorGroup(frontright,backright)
leftside = MotorGroup(frontleft,backleft)
intake = Motor(Ports.PORT5,GearSetting.RATIO_18_1,True)
catapult = Motor(Ports.PORT6,GearSetting.RATIO_18_1,False)
wings1 = DigitalOut(brain.three_wire_port.a)
wings2 = DigitalOut(brain.three_wire_port.b)
catsens = Limit(brain.three_wire_port.c)
autonSel = Optical(Ports.PORT9)
brazo = Motor(Ports.PORT8,GearSetting.RATIO_18_1,False)
wedge = DigitalOut(brain.three_wire_port.d)

player=Controller()
# endregion
# region --------driver funcs---------
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
    if player.buttonL2.pressing():
      intake.spin(FORWARD)
    elif player.buttonL1.pressing():
      intake.spin(REVERSE)
    else:
      intake.stop()
def slapper():
  toggle = 0
  brazo.set_velocity(100,PERCENT)
  while True:
    waituntil(player.buttonUp.pressing())
    if toggle == 0:
      brazo.spin_for(FORWARD,1/2,TURNS,wait=True)
      waituntil(not player.buttonUp.pressing())
      toggle = 1
    elif toggle == 1:
      brazo.spin_for(REVERSE,1/2,TURNS,wait=True)
      waituntil(not player.buttonUp.pressing())
      toggle = 0
    else: waituntil(not player.buttonUp.pressing())
def laCATAPULTA():
  while True:
    waituntil(player.buttonR2.pressing())
    if catsens.pressing():
      release()
      windup()
    else:
      windup()
    waituntil(not player.buttonR2.pressing())
def pistonManager():
  wingActivator = Event()
  wingActivator(R1Manager)
  wingActivator(LWingManager)
  wingActivator(RWingManager)
  wingActivator(wedgeF)
  wait(15,MSEC)
  wingActivator.broadcast()
def matchLoad():
  while True:
    while not player.buttonRight.pressing():
      wait(5,MSEC)
    catapult.spin(FORWARD)
    while player.buttonRight.pressing():
      wait(5,MSEC)
    catapult.stop()
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
    rightside.set_velocity(75,PERCENT)
    leftside.set_velocity(75,PERCENT)
    intake.spin_for(FORWARD,0.5,TURNS,wait=False)
    move(48)
    turn(85)
    intake.spin_for(REVERSE,1.5,TURNS,wait=False)
    wait(100,MSEC)
    move(9.4)
    intake.stop() 
    move(-30)
    wings1.set(True)
    rightside.set_velocity(75,PERCENT)
    leftside.set_velocity(75,PERCENT)
    wait(200,MSEC)
    move(29)
    wait(10,MSEC)
    wings1.set(False)
    intake.spin_for(FORWARD,0.5,TURNS,wait=False)
    move(-4.5)
    rightside.set_velocity(50,PERCENT)
    leftside.set_velocity(50,PERCENT)
    turn(-150)
    move(20)
    intake.spin_for(FORWARD,1.5,TURNS,wait=False)
    wait(100,MSEC)
    move(-4)
    turn(160)
    move(8)
    intake.spin_for(REVERSE,2,TURNS,wait=False)
    move(12)
    intake.stop()
    move(-10)
    windup()
  elif auton == 'defen':
    intake.spin_for(FORWARD,0.5,TURNS,wait=False)
    move(48)
    turn(-90)
    intake.spin_for(REVERSE,1,TURNS,wait=False)
    wait(100,MSEC)
    intake.stop()
    move(6)
    wait(100,MSEC)
    move(-25)
    turn(47)
    intake.spin_for(FORWARD,6,TURNS,wait=False)
    move(5)
    wait(100,MSEC)
    move(-5)
    turn(-45)
    wait(500,MSEC)
    catapult.spin_for(FORWARD,1,TURNS,wait=False)
    wait(100,MSEC)
    windup()
    turn(130)
    intake.spin_for(FORWARD,6,TURNS,wait=False)
    move(5)
    wait(100,MSEC)
    move(-5)
    turn(-130)
    wait(500,MSEC)
    catapult.spin_for(FORWARD,0.5,TURNS,wait=False)
  else:
    pass
# endregion 
# region --------comp funcs-----------
def autoF():
  active = Thread(autonTime)
  while (comp.is_autonomous() and comp.is_enabled()):
    wait(10,MSEC)
  active.stop()
def drivF():
  setup(1)
  controlPoint = [joystickfunc,intakefunc,laCATAPULTA,matchLoad,pistonManager]
  iters = []
  for func in controlPoint:
    active = Thread(func)
    iters.append(active)
  waituntil(not (comp.is_driver_control() and comp.is_enabled()))
  for active in iters:
    active.stop()
# endregion
# region --------other funcs----------
def waituntil(ocasion):
  while not ocasion:
    wait(5,MSEC)
def wings(exp=True):
  wings1.set(exp)
  wings2.set(exp)
def windup():
  catapult.spin(FORWARD)
  waituntil(catsens.pressing())
  catapult.stop()
  catapult.spin_for(FORWARD,1/8,TURNS,wait=True)
def release():
  catapult.spin(FORWARD)
  waituntil(not catsens.pressing())
  wait(0.5,SECONDS)
  catapult.stop()
def detectAuton():
  autonSel.set_light(LedStateType.ON)
  autonSel.set_light_power(50)
  wait(200,MSEC)
  if autonSel.is_near_object():
      color = autonSel.brightness()
      if color >= 10: # type: ignore
          brain.screen.print("defen\n")
          tmp = "defen"
      elif color < 10: # type: ignore
          brain.screen.print("offen\n")
          tmp = 'defen'
  else:
      brain.screen.print("nada\n")
      tmp = 'offen'
  autonSel.set_light(LedStateType.OFF)
  return tmp # type: ignore
def setup(value=0):
  if value == 1:
    global auton
    rightside.set_velocity(50,PERCENT)
    leftside.set_velocity(50,PERCENT)
    auton = detectAuton()
  else: 
    intake.set_velocity(100,PERCENT)#inital values de motores y whatnot
  wings(False)
  catapult.set_velocity(100,PERCENT)
def R1Manager():
  while True:
    waituntil(player.buttonR1.pressing())
    wings(True)
    waituntil(not player.buttonR1.pressing())
    wings(False)
def LWingManager():
  while True:
    waituntil(player.buttonDown.pressing() and not player.buttonR1.pressing())
    wings1.set(True)
    waituntil(not player.buttonDown.pressing())
    wings1.set(False)
def RWingManager():
  while True:
    waituntil(player.buttonB.pressing() and not player.buttonR1.pressing())
    wings2.set(True)
    waituntil(not player.buttonB.pressing())
    wings2.set(False)
def wedgeF():
  wedge.set(False)
  toggle = 0
  while True:
    waituntil(player.buttonY.pressing())
    if toggle == 0:
      wedge.set(True)
      toggle = 1
    elif toggle == 1:
      wedge.set(False)
      toggle = 0
    waituntil(not player.buttonY.pressing())
# endregion
comp = Competition(drivF,autoF)
wait(15,MSEC)

setup()