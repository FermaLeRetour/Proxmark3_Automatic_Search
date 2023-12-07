#!/usr/bin/env python3
from output_grabber import OutputGrabber
from pyfirmata import Arduino, util
import pm3
import argparse
import subprocess
import re
import time
#import threading
import keyboard

#def listen_for_keypress():
#    while True:
#        if keyboard.is_pressed('f'):
#            #crack_key(f,port)
#            print("pressed")


def connect_proxmark(port):

    try:
        p=pm3.pm3(port)
    except:
        print("Erreur lors de la tentative de connexion au proxmark\nSecond Essai ...")
    return p

def card_search(command,args):

    force=args.key
    output_file=args.output_file
    port=args.port

    p=connect_proxmark(port)
     #Initialize connection to the proxmark
    print('\n')
    print('Script lancé') 
    print('\n') 

    button_pin=board.get_pin('d:11:i') #we take D11 as input for the button
    led_pin=board.get_pin('d:13:o') #We take the led from the Latte Panda board


    button_state=False
    pressed=0

    try:
        while True:   

            button_state_new=button_pin.read()
            if button_state!=button_state_new:
                button_state=button_state_new


                if button_state:
                    pressed=pressed+1

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


                        if "MIFARE Classic" in out.capturedtext and force:
                            
                            p=None                           
                            crack_key(f,port)
                            time.sleep(5)
                            p=connect_proxmark(port)

                        f.write("\n"+"-"*150+"\n")
                        time.sleep(1)

                    else:
                        print("Recherche ...                               " , end="\r")
            else:
                print('Appuyer sur le bouton pour commencer ...                    ',end="\r")
                led_pin.write(0)
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        led_pin.write(0)
        board.exit()

def crack_key(f,port):
    print("Essaie de trouver les clés ...")

    try:
        crack= subprocess.run(['/home/quentin/Documents/proxmark3/pm3','-c','hf mf autopwn','-p',port], stdout=subprocess.PIPE,timeout=timeout)
        if crack.returncode==0:
            pattern = r'(/[^\n]+\.bin)'
            pattern2 = r'(/[^\n]+\.json)'
            file_paths = re.findall(pattern, crack.stdout.decode('utf-8'))
            file_paths2 = re.findall(pattern2, crack.stdout.decode('utf-8'))
            result=f"Clé trouvée : {file_paths[0]}\nDump de la carte : {file_paths[1]},{file_paths2[0]}\n"
            print(result)
            f.write(result)
        else:
            print("Erreur n'a pas pu trouver les clés")
    except subprocess.TimeoutExpired:
        print("TimeOut")




def parse_arguments():

    parser = argparse.ArgumentParser(description="Auto-Search cards -h, -hf, and -lf options")
    parser.add_argument('-hf', '--high_f',action='store_true', help="Search for high frequency cards")
    parser.add_argument('-lf', '--low_f',action='store_true',  help="Search for low frequency cards")
    parser.add_argument('-a','--all',action='store_true',help="Search for all frequencies")
    parser.add_argument('-k','--key',action='store_true',help="Try to crack the key")
    parser.add_argument('-14a','--14acard',action='store_true',help="Search for ISO 14443a cards (Mifare...)")
    parser.add_argument('-t','--timeout',type=int,help="TimeOut to crack the keys")
    parser.add_argument('-o','--output_file',required=True, type=str, help="Output files")
    parser.add_argument('-p','--port',required=True, type=str, help="Proxmark port to connect to ex(/dev/ttyACM1 or bt:20:23:01:03:04:15)")
    args = parser.parse_args()





    if args.high_f:
        command='hf search'
        print("Mode : Haute Frequence")
    elif args.low_f:
        command='lf search'
        print("Mode : Basse Fréquence")
    elif args.all:
        command='auto'
        print("Mode : Toutes les frequences")
    else:
        command='hf 14a info'
        print("Mode : Carte ISO 14443a")

    print(f"Cherche les clés: {args.key}")

    return args,command


if __name__ == '__main__':


    args,command=parse_arguments() #Parse arguments


    if args.timeout:
        timeout=args.timeout
    else:
        timeout=15

    #keypress_thread=threading.Thread(target=listen_for_keypress)
    #keypress_thread.start()

    board=Arduino('/dev/ttyACM0') #Initialize the connection to the Arduino board
    it=util.Iterator(board)
    it.start()

    card_search(command,args)





