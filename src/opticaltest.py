from vex import *

brain=Brain()

opt1 = Optical(Ports.PORT9)

player=Controller()

def main():
    opt1.set_light(LedStateType.ON)
    opt1.set_light_power(25)
    wait(20,MSEC)
    if opt1.is_near_object():
        color = opt1.brightness()
        if color >= 10:
            tmp = "vincent"
        elif color < 10:
            tmp = 'kevin'
    else:
        tmp = 'armando'
    brain.screen.print(tmp + '\n')


while True:
    wait(2,SECONDS)
    main()