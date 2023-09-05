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


        
