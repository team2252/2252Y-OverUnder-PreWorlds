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
trackwidth = 12.25

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
catapult2 = Motor(Ports.PORT7,GearSetting.RATIO_36_1,True)
catapult = MotorGroup(catapult2,catapult2)
wings1 = DigitalOut(brain.three_wire_port.a)
wings2 = DigitalOut(brain.three_wire_port.b)
catsens = Limit(brain.three_wire_port.c)
autonSel = Optical(Ports.PORT9)
brazo = Motor(Ports.PORT10,GearSetting.RATIO_18_1,False)
wedge = DigitalOut(brain.three_wire_port.d)
gyro = Inertial(Ports.PORT11)

player=Controller()

gyro.calibrate()
while gyro.is_calibrating():
  wait(15,MSEC)
# endregion
# region --------driver funcs---------
def endgameAlert():
  wait(80,SECONDS)
  player.rumble('..-')
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
def laCATAPULTA():
  while True:
    while not player.buttonR2.pressing():
      wait(5,MSEC)
    if catsens.pressing():
      release()
      wait(15,MSEC)
      windup()
    else:
      windup()
    while player.buttonR2.pressing():
      wait(5,MSEC)
def wingManager():
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
def hangfunc():
  brazo.set_velocity(75,PERCENT)
  brazo.spin(REVERSE)
  wait(0.25,SECONDS)
  brazo.stop()
  windup()
  while True:
    if player.buttonLeft.pressing():
      brazo.spin(FORWARD)
    elif player.buttonUp.pressing():
      brazo.spin(REVERSE)
    else:
      brazo.stop()
# endregion
# region --------auton funcs----------
def process(val):
  if val > 0: return val
  elif val < 0: return 360 - val
  else: return 0
def move(dis=float(24)):
  leftside.set_velocity(75,PERCENT)
  rightside.set_velocity(75,PERCENT)
  factor=5.5
  leftside.spin_for(FORWARD,dis/factor,TURNS,wait=False)
  rightside.spin_for(FORWARD,dis/factor,TURNS,wait=True)
  wait(5,MSEC)
def smove(dis=float(24)):
  leftside.set_velocity(10,PERCENT)
  rightside.set_velocity(10,PERCENT)
  factor=5.5
  leftside.spin_for(FORWARD,dis/factor,TURNS,wait=False)
  rightside.spin_for(FORWARD,dis/factor,TURNS,wait=True)
  wait(5,MSEC)
def turn(theta=90):
  gyro.set_heading(0)
  rightside.set_velocity(30,PERCENT)
  leftside.set_velocity(30,PERCENT)
  turnAmount = calcRot(theta)
  leftside.spin_for(FORWARD,turnAmount,TURNS,wait=False)
  rightside.spin_for(REVERSE,turnAmount,TURNS,wait=True)
  wait(5,MSEC)
  finetune(theta)
def pturn(theta=90):
  gyro.set_heading(0)
  rightside.set_velocity(45,PERCENT)
  leftside.set_velocity(45,PERCENT)
  turnAmount = abs(calcRot(theta)*2)
  if theta < 0: leftside.set_stopping(HOLD); rightside.spin_for(FORWARD,turnAmount,TURNS)
  else: rightside.set_stopping(HOLD); leftside.spin_for(FORWARD,turnAmount,TURNS)
  leftside.set_stopping(BRAKE)
  rightside.set_stopping(BRAKE)
  wait(5)
  finetune(theta)
def rpturn(theta=90):
  gyro.set_heading(0)
  rightside.set_velocity(45,PERCENT)
  leftside.set_velocity(45,PERCENT)
  turnAmount = -abs(calcRot(theta)*2)
  if theta < 0: rightside.set_stopping(HOLD); leftside.spin_for(FORWARD,turnAmount,TURNS)
  else: leftside.set_stopping(HOLD); rightside.spin_for(FORWARD,turnAmount,TURNS)
  leftside.set_stopping(BRAKE)
  rightside.set_stopping(BRAKE)
  wait(5)
  finetune(theta)
def sturn(theta=90):
  gyro.set_heading(0)
  rightside.set_velocity(20,PERCENT)
  leftside.set_velocity(20,PERCENT)
  turnAmount = calcRot(theta)
  leftside.spin_for(FORWARD,turnAmount,TURNS,wait=False)
  rightside.spin_for(REVERSE,turnAmount,TURNS,wait=True)
  wait(5,MSEC)
  if theta < 0: finetune(theta)
  elif theta > 0: finetune(theta)
def finetune(val):
  val = process(val)
  rightside.set_velocity(5,PERCENT)
  leftside.set_velocity(5,PERCENT)
  if (val + 1) < gyro.heading():
    leftside.spin(REVERSE)
    rightside.spin(FORWARD)
  elif (val - 1) > gyro.heading():
    leftside.spin(FORWARD)
    rightside.spin(REVERSE)
  while not (gyro.heading() < (val - 1) or gyro.heading() > (val + 1)):
    wait(5,MSEC)
  leftside.stop()
  rightside.stop()
def autonTime():
  setup(1)
  if auton == 'offen':
   rightside.set_velocity(75,PERCENT)
   leftside.set_velocity(75,PERCENT)
   move(47)
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
   turn(150)
   move(8)
   intake.spin_for(REVERSE,3,TURNS,wait=True)
   move(13)
   intake.stop()
   move(-28)
   
   


  elif auton == 'defen':
    move(3)
    brazo.spin_for(FORWARD,0.6,TURNS,wait=False)
    wait(1000,MSEC)
    move(3)
    sturn(160)
    rightside.set_velocity(75,PERCENT)
    leftside.set_velocity(75,PERCENT)
    brazo.stop()
    brazo.spin_for(REVERSE,0.5,TURNS,wait=True)
    brazo.stop()
    turn(10)
    intake.spin_for(FORWARD,3,TURNS,wait=False)
    move(5)
    wait(10,MSEC)
    move(-7)
    turn(-160)
    move(5)
    intake.spin_for(REVERSE,3,TURNS,wait=True)
    move(8)
    wait(10,MSEC)
    move(-10)
    turn(-50)
    wait(10,MSEC)
    move(-25)
    turn(-25)
    move(-19)
    wait(10,MSEC)
    smove(-5)
  else:
    pass
# endregion 
# region --------comp funcs-----------
def startDriver():
  driver.broadcast()
def autoF():
  active = Thread(autonTime)
  while (comp.is_autonomous() and comp.is_enabled()):
    wait(10,MSEC)
  active.stop()
def drivF():
  setup(1)
  active = Thread(startDriver)
  while comp.is_driver_control() and comp.is_enabled():
    wait(5,MSEC)
  active.stop()
# endregion
# region --------other funcs----------
def wings(exp=True):
  wings1.set(exp)
  wings2.set(exp)
def windup():
  catapult.spin(FORWARD)
  while (not catsens.pressing()):
    wait(5,MSEC)
  catapult.spin_for(FORWARD,1/6,TURNS,wait=True)
def release():
  catapult.spin(FORWARD)
  while catsens.pressing():
    wait(5,MSEC)
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
  catapult.set_stopping(COAST)
  catapult.set_velocity(100,PERCENT)
def R1Manager():
  while True:
    while not player.buttonR1.pressing():
      wait(5,MSEC) 
    wings(True)
    while player.buttonR1.pressing():
      wait(5,MSEC)
    wings(False)
def LWingManager():
  while True:
    while not (player.buttonDown.pressing() and not player.buttonR1.pressing()):
      wait(5,MSEC)
    wings1.set(True)
    while player.buttonDown.pressing():
      wait(5,MSEC)
    wings1.set(False)
def RWingManager():
  while True:
    while not (player.buttonB.pressing() and not player.buttonR1.pressing()):
      wait(5,MSEC)
    wings2.set(True)
    while player.buttonB.pressing():
      wait(5,MSEC)
    wings2.set(False)
def wedgeF():
  wedge.set(False)
  toggle = 0
  while True:
    while not (player.buttonY.pressing()):
      wait(5,MSEC)
    if toggle == 0:
      wedge.set(True)
      toggle = 1
    elif toggle == 1:
      wedge.set(False)
      toggle = 0
    while player.buttonY.pressing():
      wait(5,MSEC)
def calcRot(val=float(0)):
  rCirc = trackwidth * 3.14159
  return ((val/360)*rCirc/12.556)*7/3
def calcArc(val=float(0)):
  return val/12.556*7/3
# endregion
driver = Event()
comp = Competition(drivF,autoF)
driver(endgameAlert)
driver(joystickfunc)
driver(intakefunc)
driver(laCATAPULTA)
driver(matchLoad)
driver(wingManager)
driver(hangfunc)
wait(15,MSEC)

setup()