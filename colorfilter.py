
f = open('setting.txt', 'r')

try :
    filter_storage = eval(f.readline())
    red =  filter_storage[2]
    blue =  filter_storage[3]
    green = filter_storage[4]
    yellow = filter_storage[5]

    
except:

    red =  [(160, 70,70), (180, 255, 255)]
    blue =  [(100, 100, 100), (120,255,255)]
    green = [(70, 70, 70), (80, 255, 255)]
    yellow = [(20, 70, 70), (60, 255, 255)] 

f.close()

