#!/usr/bin/env python3

import pm3
from output_grabber import OutputGrabber
import argparse
import subprocess
import re
import time




def card_search(command,output_file,force):

    p=pm3.pm3("/dev/ttyACM0")
    print('\n')
    print('Searching for cards...') 
    print('\n') 

    while True:   
        out = OutputGrabber()   
        with out:
            p.console(command)
        with open(output_file,'a') as f:
            if '+' in out.capturedtext:
                print("Carte trouvée :")
                print(out.capturedtext)
                f.write("Carte trouvée :\n")
                f.write(f"Date : {time.ctime(time.time())}")
            for line in out.capturedtext.split('\n'):
                if '+' in line:
                    f.write(line + '\n')

            f.write("\n")

            if "MIFARE Classic" in out.capturedtext and force:
                p=None
                crack_key(f)
                p=pm3.pm3("/dev/ttyACM0")


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



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Auto-Search cards -h, -hf, and -lf options")
    parser.add_argument('-hf', '--high_f',action='store_true', help="Search for high frequency cards")
    parser.add_argument('-lf', '--low_f',action='store_true',  help="Search for low frequency cards")
    parser.add_argument('-a','--all',action='store_true',help="Search for all frequencies")
    parser.add_argument('-k','--key',action='store_true',help="Try to crack the key")
    parser.add_argument('-o','--output_file',required=True, type=str, help="Output files")
    args = parser.parse_args()

    if args.high_f:
        command='hf search'
    elif args.low_f:
        command='lf search'
    else:
        command='auto'



    card_search(command,args.output_file,args.key)






