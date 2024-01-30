# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       arnaldoalicea                                                #
# 	Created:      9/5/2023, 4:10:45 PM                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #
trackwidth = 12.25
wheelbase = 10
wheeldiam = 4

autonFile = open("skillAuton.csv", 'r')
global autonDat
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
Rside = MotorGroup(frontright,backright)
Lside = MotorGroup(frontleft,backleft)
intake = Motor(Ports.PORT5,GearSetting.RATIO_18_1,True)
catapult1 = Motor(Ports.PORT6,GearSetting.RATIO_18_1,False)
catapult2 = Motor(Ports.PORT7,GearSetting.RATIO_36_1,True)
catapult = MotorGroup(catapult2,catapult2)
wings1 = DigitalOut(brain.three_wire_port.a)
wings2 = DigitalOut(brain.three_wire_port.b)
catsens = Limit(brain.three_wire_port.c)
autonSel = Optical(Ports.PORT9)
brazo = Motor(Ports.PORT10,GearSetting.RATIO_18_1,False)
untip = DigitalOut(brain.three_wire_port.d)
gyro = Inertial(Ports.PORT11)
Blocker = DigitalOut(brain.three_wire_port.e)
robot = SmartDrive(Lside,Rside,gyro,wheeldiam*math.pi,trackwidth,wheelbase,INCHES,7/3)

player=Controller()

robot.g.calibrate()
while robot.g.is_calibrating():
  wait(15,MSEC)
# endregion
# region --------driver funcs---------
def endgameAlert():
  wait(80,SECONDS)
  player.rumble('..-')
  wait(15,SECONDS)
  player.rumble('---')
def joystickfunc():
  Lside.spin(FORWARD)
  Rside.spin(FORWARD)
  while True:
    Lside.set_velocity(player.axis3.position()+player.axis1.position(),PERCENT)
    Rside.set_velocity(player.axis3.position()-player.axis1.position(),PERCENT)
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
  global catActiv
  while True:
    catActiv = True
    while (not player.buttonR2.pressing()) and catActiv:
      unwind()
    if catsens.pressing() and player.buttonR2.pressing() and catActiv:
      release()
      wait(15,MSEC)
      windup()
    elif player.buttonR2.pressing() and catActiv:
      windup()
    while player.buttonR2.pressing() and catActiv:
      unwind()
def wingManager():
  wingActivator = Event()
  wingActivator(R1Manager)
  wingActivator(LWingManager)
  wingActivator(RWingManager)
  wingActivator(untipF)
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
def Block():
 while True:
    while not player.buttonY.pressing():
      wait(5,MSEC) 
    Blocker.set(True)
    while player.buttonY.pressing():
      wait(5,MSEC)
    while not player.buttonY.pressing():
      wait(5,MSEC) 
    Blocker.set(False)
    while player.buttonY.pressing():
      wait(5,MSEC)
# endregion
# region --------auton funcs----------
def process(val):
  if val > 0: return val
  elif val < 0: return 360 - val
  else: return 0
def move(dis=float(24)):
  vel = 80
  robot.set_drive_velocity(vel,PERCENT)
  robot.drive_for(FORWARD,dis,wait=True)
  wait(5,MSEC)
def smove(dis=float(24)):
  vel = 20
  robot.set_drive_velocity(vel,PERCENT)
  robot.drive_for(FORWARD,dis,wait=True)
def turn(theta=90):
  vel = 37
  robot.set_turn_velocity(vel,PERCENT)
  robot.turn_for(RIGHT,theta,wait=True)
def pturn(theta=90):
  # gyro.set_heading(0)
  Rside.set_velocity(45,PERCENT)
  Lside.set_velocity(45,PERCENT)
  turnAmount = abs(calcPTurn(theta))
  if theta < 0: Lside.set_stopping(HOLD); Rside.spin_for(FORWARD,turnAmount,TURNS)
  else: Rside.set_stopping(HOLD); Lside.spin_for(FORWARD,turnAmount,TURNS)
  Lside.set_stopping(BRAKE)
  Rside.set_stopping(BRAKE)
  wait(5)
  # finetune(theta)
def rpturn(theta=90):
  # gyro.set_heading(0)
  Rside.set_velocity(45,PERCENT)
  Lside.set_velocity(45,PERCENT)
  turnAmount = -abs(calcPTurn(theta))
  if theta < 0: Rside.set_stopping(HOLD); Lside.spin_for(FORWARD,turnAmount,TURNS)
  else: Lside.set_stopping(HOLD); Rside.spin_for(FORWARD,turnAmount,TURNS)
  Lside.set_stopping(BRAKE)
  Rside.set_stopping(BRAKE)
  wait(5)
  # finetune(theta)
def sturn(theta=90):
  vel = 20
  robot.set_turn_velocity(vel,PERCENT)
  robot.turn_for(RIGHT,theta,wait=True)
def aturn(theta=90,pivdis=float(5)):
  gyro.set_heading(0)
  vel = 55
  velocity(vel)
  if theta < 0:
    turnR = abs(calcArc(theta,pivdis+trackwidth))
    turnL = abs(calcArc(theta,pivdis))
    veL = vel * (turnL/turnR)
    veR = vel
  else:
    turnL = abs(calcArc(theta,pivdis+trackwidth))
    turnR = abs(calcArc(theta,pivdis))
    veL = vel
    veR = vel * (turnR/turnL)
  Rside.spin_for(FORWARD,turnR,TURNS,veR,PERCENT,False)
  Lside.spin_for(FORWARD,turnL,TURNS,veL,PERCENT,False)
  wait(5,MSEC)
def raturn(theta=90,pivdis=float(5)):
  # gyro.set_heading(0)
  vel = 55
  Rside.set_velocity(vel,PERCENT)
  Lside.set_velocity(vel,PERCENT)
  if theta > 0:
    turnR = abs(calcArc(theta,pivdis+trackwidth))
    turnL = abs(calcArc(theta,pivdis))
    veL = vel * (turnL/turnR)
    veR = vel
  else:
    turnL = abs(calcArc(theta,pivdis+trackwidth))
    turnR = abs(calcArc(theta,pivdis))
    veL = vel
    veR = vel * (turnR/turnL)
  Rside.spin_for(REVERSE,turnR,TURNS,veR,PERCENT,False)
  Lside.spin_for(REVERSE,turnL,TURNS,veL,PERCENT,False)
  wait(5,MSEC)
def velocity(val=100):
  Rside.set_velocity(val,PERCENT)
  Lside.set_velocity(val,PERCENT)
def autonTime():
  setup(1)
  gyro.set_heading(0)
  turn(-30)
  move(-20)
  turn(30)
  # move(-5)
  # turn(140)
  # move(63)
  # turn(85)
  # move(39)
  # wings(True)
  # move(45)
  # wait(10,MSEC)
  # move(-25)
  # wings(False)
  # turn(90)
  # move(27)
  # turn(-150)
  # wings(True)
  # aturn(90,10)
  # move(-7)
  # move(15)
  # wings(False)
  # move(-25)
  # turn(90)
  # move(-27)
  # wings(True)
  # aturn(-90,15)
  # move(-15)
  # move(15)
  # move(-10)
  # wings(False)
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
    unwind()
  catapult.spin_for(FORWARD,1/7,TURNS,wait=False)
  while catapult.is_spinning():
    unwind()
def unwind():
  catActiv = False
  if player.buttonX.pressing():
    catapult.spin(REVERSE)
    while player.buttonX.pressing():
      wait(5)
    catapult.stop()
  wait(5)
def release():
  catapult.spin(FORWARD)
  while catsens.pressing():
    unwind()
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
    Rside.set_velocity(50,PERCENT)
    Lside.set_velocity(50,PERCENT)
    auton = detectAuton()
    autonDat = getData(autonFile)
  else: 
    intake.set_velocity(100,PERCENT)#inital values de motores y whatnot
  wings(False)
  catapult.set_stopping(HOLD)
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
def untipF():
  untip.set(False)
  while True:
    while not (player.buttonUp.pressing()):
      wait(5,MSEC)
    untip.set(True)
    while player.buttonUp.pressing():
      wait(5,MSEC)
    untip.set(False)
def calcPTurn(val=float(0)):
  rCirc = trackwidth * math.pi * 2
  turnDist = ((val/360)*rCirc)
  turnAmnt = turnDist/wheeldiam*math.pi
  return turnAmnt*7/3
def calcRot(val=float(0)):
  rCirc = trackwidth * math.pi
  return ((val/360)*rCirc/12.556)*7/3
def calcArc(degs=0,dis=float(0)):
  val = ((degs * math.pi) / 180) * dis
  return val/12.556*7/3
def getData(var):
  dat = []
  dat2 = []
  for line in var.readlines():
    dat2.append(line.split(','))
    dat.append(dat2)
    dat2.clear()
  return dat
# endregion
def autonTest():
  aturn(-90,15)
driver = Event()
comp = Competition(drivF,autoF)
driver(endgameAlert)
driver(joystickfunc)
driver(intakefunc)
driver(laCATAPULTA)
driver(matchLoad)
driver(wingManager)
driver(Block)
wait(15,MSEC)

setup()