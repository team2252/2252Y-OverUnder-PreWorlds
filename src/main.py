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
centerleft = Motor(Ports.PORT20,GearSetting.RATIO_6_1,False)
centerright = Motor(Ports.PORT19,GearSetting.RATIO_6_1,True)
Rside = MotorGroup(frontright,backright,centerright)
Lside = MotorGroup(frontleft,backleft,centerleft)
intake = Motor(Ports.PORT5,GearSetting.RATIO_6_1,False)
catapult = Motor(Ports.PORT6,GearSetting.RATIO_36_1,False)
wings1 = DigitalOut(brain.three_wire_port.a)
wings2 = DigitalOut(brain.three_wire_port.b)
autonSel = Optical(Ports.PORT9)
untip = DigitalOut(brain.three_wire_port.d)
gyro = Inertial(Ports.PORT11)
Blocker = DigitalOut(brain.three_wire_port.e)
catsens = Rotation(Ports.PORT7, False)

player=Controller()

gyro.calibrate()
while gyro.is_calibrating():
  wait(15,MSEC)
def rotcata():
  global minrot, maxrot
  minrot = catsens.angle()
  maxrot = catsens.angle()
  catapult.spin_for(FORWARD,1,TURNS,wait=False)
  while True:
    if catsens.angle() < minrot: minrot = catsens.angle()
    if catsens.angle > maxrot: maxrot = catsens.angle()
    if catapult.():
      break
    wait(5)
  catapult.stop()
  player.screen.print("cali ready")
  while True:
    while not player.buttonRight.pressing():
      wait(5)
    catapult.spin(FORWARD)
    catapult.set_stopping(HOLD)
    while catsens.angle() < maxrot:
      wait(5)
    catapult.stop()
    while player.buttonRight.pressing():
      wait(5)
    while not player.buttonRight.pressing():
      wait(5)
    catapult.set_stopping(COAST)
    while player.buttonRight.pressing():
      wait(5)
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
  while True:
    while not player.buttonR2.pressing():
      wait(5)
    catapult.spin(FORWARD)
    while player.buttonR2.pressing():
      wait(5)
    while not player.buttonR2.pressing():
      wait(5)
    catapult.stop()
    while player.buttonR2.pressing():
      wait(5)
def pneumaticManager():
  activator = Event()
  activator(R1Manager)
  activator(LWingManager)
  activator(RWingManager)
  activator(untipF)
  wait(15,MSEC)
  activator.broadcast()
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
def velocity(vel):
  Lside.set_velocity(vel,PERCENT)
  Rside.set_velocity(vel,PERCENT)
def move(dis=float(24)):
  vel = 80
  velocity(vel)
  tAmnt = dis/7
  Lside.spin_for(FORWARD,tAmnt,TURNS,wait=False)
  Rside.spin_for(FORWARD,tAmnt,TURNS,wait=True)
  wait(5,MSEC)
def smove(dis=float(24)):
  vel = 10
  velocity(vel)
  factor=7
  Lside.spin_for(FORWARD,dis/factor,TURNS,wait=False)
  Rside.spin_for(FORWARD,dis/factor,TURNS,wait=True)
  wait(5,MSEC)
def nmove(dis=float(24)):
  vel = 20
  velocity(vel)
  factor=7
  Lside.spin_for(FORWARD,dis/factor,TURNS,wait=False)
  Rside.spin_for(FORWARD,dis/factor,TURNS,wait=True)
  wait(5,MSEC)
def turn(theta=90):
  vel = 40
  gyro.set_heading(0)
  velocity(vel)
  turnAmount = calcRot(theta)
  Lside.spin_for(FORWARD,turnAmount,TURNS,wait=False)
  Rside.spin_for(REVERSE,turnAmount,TURNS,wait=True)
  wait(5,MSEC)
  finetune(theta)
def pturn(theta=90):
  velocity(45)
  gyro.set_heading(0)
  turnAmount = abs(calcRot(theta)*2)
  if theta < 0: Lside.set_stopping(HOLD); Rside.spin_for(FORWARD,turnAmount,TURNS)
  else: Rside.set_stopping(HOLD); Lside.spin_for(FORWARD,turnAmount,TURNS)
  Lside.set_stopping(BRAKE)
  Rside.set_stopping(BRAKE)
  wait(5)
  finetune(theta)
def rpturn(theta=90):
  velocity(45)
  gyro.set_heading(0)
  turnAmount = -abs(calcRot(theta)*2)
  if theta < 0: Rside.set_stopping(HOLD); Lside.spin_for(FORWARD,turnAmount,TURNS)
  else: Lside.set_stopping(HOLD); Rside.spin_for(FORWARD,turnAmount,TURNS)
  Lside.set_stopping(BRAKE)
  Rside.set_stopping(BRAKE)
  wait(5)
  finetune(theta)
def sturn(theta=90):
  vel = 20
  gyro.set_heading(0)
  velocity(vel)
  turnAmount = calcRot(theta)
  Lside.spin_for(FORWARD,turnAmount,TURNS,wait=False)
  Rside.spin_for(REVERSE,turnAmount,TURNS,wait=True)
  wait(5,MSEC)
  finetune(theta)
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
  Lside.spin_for(FORWARD,turnL,TURNS,veL,PERCENT,True)
  wait(5,MSEC)
def raturn(theta=90,pivdis=float(5)):
  gyro.set_heading(0)
  vel = 55
  velocity(vel)
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
  Lside.spin_for(REVERSE,turnL,TURNS,veL,PERCENT,True)
  wait(5,MSEC)
def finetune(val):
  val = process(val)
  Rside.set_velocity(5,PERCENT)
  Lside.set_velocity(5,PERCENT)
  if (val + 1) < gyro.heading():
    Lside.spin(REVERSE)
    Rside.spin(FORWARD)
  elif (val - 1) > gyro.heading():
    Lside.spin(FORWARD)
    Rside.spin(REVERSE)
  while not (gyro.heading() < (val - 1) or gyro.heading() > (val + 1)):
    wait(5,MSEC)
  Lside.stop()
  Rside.stop()
def releaseIntake():
  Blocker.set(True)
  wait(100)
  Blocker.set(False)
def tmove(time):
  velocity(80)
  Lside.spin(FORWARD)
  Rside.spin(FORWARD)
  wait(time,SECONDS)
  Lside.stop()
  Rside.stop()
def rtmove(time):
  velocity(80)
  Lside.spin(REVERSE)
  Rside.spin(REVERSE)
  wait(time,SECONDS)
  Lside.stop()
  Rside.stop()
def autonTime():
  setup(1)
  if auton == 'offen':
    move(5)
    intake.spin_for(FORWARD,5,TURNS,wait=False)
    wait(300,MSEC)
    move(-34)
    raturn(-90,10)
    move(-18)
    move(5)
    turn(180)
    intake.spin_for(REVERSE,2,TURNS,wait=True)
    move(8)
    wait(100,MSEC)
    move(-7)
    turn(-90)
    rtmove(0.5)
    move(30)
    turn(18)
    intake.spin_for(FORWARD,12,TURNS,wait=False)
    move(35)
    turn(150)
    intake.spin_for(REVERSE,3,TURNS,wait=True)
    move(10)
    turn(-120)
    intake.spin_for(FORWARD,7,TURNS,wait=False)
    move(27)
    turn(150)
    rtmove(0.5)
    wings(True)
    intake.spin_for(REVERSE,2,TURNS,wait=False)
    move(46)
    wait(100,MSEC)
    move(-10)
    wings(False)

      # turn(150)
    # wings1.set(True)
    # move(20)
    # intake.spin_for(REVERSE,3,TURNS,wait=False)
    # move(18)
    # wings1.set(False)
    # move(-6)
    # turn(130)
    # move()

  

    # catapult.spin_for(FORWARD,0.55,TURNS,wait=False)
    # move(12)
    # intake.spin_for(REVERSE,6,TURNS,wait=False,velocity=60)
    # move(17)
    # sturn(-37)
    # intake.spin_for(FORWARD,14,TURNS,wait=False)
    # move(50)
    # turn(130)
    # wings1.set(True)
    # wait(100,MSEC)
    # move(12)
    # intake.spin_for(REVERSE,5,TURNS,wait=True)
    # move(20)
    # wait(100,MSEC)
    # wings1.set(False)
    # move(-20)
    # turn(145)
    # intake.spin_for(FORWARD,7,TURNS,wait=False)
    # move(14)
    # wait(100,MSEC)
    # move(-7)
    # turn(-130)
    # wait(100,MSEC)
    # move(14)
    # intake.spin_for(REVERSE,3,TURNS,wait=True)
    # move(17)
    # move(-7)
    # wait(100,MSEC)
    # Blocker.set(False)
  elif auton == 'defen':
    wings2.set(True)
    wait(200,MSEC)
    wings2.set(False)
    move(6)
    turn(-60)
    move(11)
    wings1.set(True)
    wait(300,MSEC)
    turn(-50)
    wings1.set(False)
    wait(200,MSEC)
    turn(40)
    move(-20)
    wait(100,MSEC)
    turn(-30+180)
    Blocker.set(True)
    wait(500,MSEC)
    intake.spin(REVERSE)
    move(30)
    Blocker.set(False)
    wait(0.75,SECONDS)
    intake.stop()
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
  else: 
    intake.set_velocity(100,PERCENT)#inital values de motores y whatnot
  wings(False)
  catapult.set_stopping(COAST)
  catapult.set_velocity(65,PERCENT)
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
    while not (player.buttonUp.pressing() or player.buttonX.pressing()):
      wait(5,MSEC)
    if player.buttonX.pressing():
      Blocker.set(True)
      wait(400)
    untip.set(True)
    if player.buttonX.pressing():
      wait(25)
      Blocker.set(False)
    while player.buttonUp.pressing() or player.buttonX.pressing():
      wait(5,MSEC)
    untip.set(False)
def calcRot(val=float(0)):
  rCirc = trackwidth * math.pi
  return ((val/360)*rCirc/12.556)*7/3
def calcArc(degs=0,dis=float(0)):
  val = ((degs * math.pi) / 180) * dis
  return val/12.556*7/3
# endregion
def autonTest():
  aturn(-90,15)
driver = Event()
comp = Competition(drivF,autoF)
driver(endgameAlert)
driver(joystickfunc)
driver(intakefunc)
driver(laCATAPULTA)
driver(pneumaticManager)
driver(Block)
driver(rotcata)
wait(15,MSEC)

setup()