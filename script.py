import argparse
import json
import sys
import os
import shutil
import time 
import subprocess
import csv


parser = argparse.ArgumentParser(description='Bitrate Profiling')
parser.add_argument('video', help='Input Video')
parser.add_argument('--target', type=str, default='1280x720', help='Target Resolution')
parser.add_argument('--crf', type=int, default=28, help='CRF value')
parser.add_argument('--bitrate', type=str, default='1000K', help='Target Bitrate')
parser.add_argument('--bufsize', type=int, default=2000, help='Target bufsize')
parser.add_argument('--maxrate', type=int, default=1000, help='Target maxrate')
parser.add_argument('--preset', type=str, default='medium', help='Preset value')
parser.add_argument('--filter', type=str, default='1,2,3,4,5,6,7,8,9', help='Cases to consider')
args = parser.parse_args()

def createOutputDirectory(output = 'Outputs'):
    #check if output path exists
    if os.path.exists(output):
        shutil.rmtree(output)
    #make an output folder 
    os.mkdir('Outputs')

def removeResult(fileName = 'result.csv'):
    #check if output path exists
    if os.path.exists(fileName):
        os.remove(fileName)
        
def runCase(case):
    id = case['id'];
    title = case['title']
    commands = getValidCommands(case['commands'], id)
    
    start = time.time()
    for command in commands:
        subprocess.call(command, shell=True)
    end = time.time()

    duration = end - start

    #Save the results to CSV
    writeResult(id, title, duration)

    #cleanup in case of 2 paas 
    if('2 Pass' in title):
        subprocess.call('rm -rf x265_2pass*', shell=True)
    

def getValidCommands(commands, id):
    validCommands = []
    for command in commands:
        command = command.replace('<input>', input + '/' + args.video)
        command = command.replace('<output>', '{}/{}.mp4'.format(output, id))
        command = command.replace('<resolution>', args.target)
        command = command.replace('<crf>', str(args.crf))
        command = command.replace('<bitrate>', str(args.bitrate))
        command = command.replace('<maxrate>', str(args.maxrate))
        command = command.replace('<bufsize>', str(args.bufsize))
        command = command.replace('<preset>', args.preset)
        validCommands.append(command)

    return validCommands

def writeResult(id, title, duration):
    with open('result.csv', 'a') as csvfile:
        csvfile.write('{},{},{}\n'.format(id,title,duration))

#global variables 
input = 'Inputs'
output = 'Outputs'
cases = None #config is a list of dictionery. Each dictionery item is a case with an id, a title and the commands to run
with open('cases.json', 'r') as f:
    cases = json.load(f)

filterList = [int(x) for x in args.filter.split(',')]
if(len(filterList) == 0):
    exit('filter List cannot be empty')

cases = filter(lambda case: case['id'] in filterList, cases)


#Create the output folder 
createOutputDirectory(output)

#Remove the results file 
removeResult()

#add a new results file
writeResult('id', 'title', 'duration')

#run the cases
for case in cases:
    runCase(case)

