import time
import serial


ser = serial.Serial(
    port='\\.\COM7',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)




print('Com Port: ' + ser.portstr + ' opened')





print('Use WASD to choose the direction you want the robot to go in: ')

userInput = 1

while 1 :
    userInput = input ('Enter Direction: ')
    if userInput == 'x':
        ser.close()
        exit()
    else:
        #send the character to the device
        ser.write(userInput.encode('utf-8'))
        #x = ser.readline(100);
        #print(x);
        

