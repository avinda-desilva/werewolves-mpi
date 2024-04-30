#Author: Mike Jacobi
#Test and Update: Xu Zhang
#Thanks to Jeff Knockel, Geoff Reedy, Matthew Hall, and Geoff Alexander for
#suggesting fixes to communication.py

#Upgraded Werewolves to work with MPI
#Virtual Werewolves
#Collaborators: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#This script has generic helper functions used by the Mafia server and clients

#Copyright (c) 2012 Mike Jacobi, Xu Zhang, Roya Ensafi, Jed Crandall, Avinda De Silva, Clay Castronovo
#This file is part of Virtual Werewolf Game.

#Virtual werewolf is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#Virtual werewolf is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Virtual werewolf.  If not, see <http://www.gnu.org/licenses/>.


import os
import time
import threading
import random
from threading import Thread

# Import MPI Library
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

all = {}

pipeRoot = '/home/moderator/pipes/'
logName = ''
mLogName = ''
conns = {}
allowed = {}
logChat = 0
currentTime = 0

readVulnerability = 1
readVulnerability_2 = 1
imposterMode = 1
isSilent = 1
def setVars(passedReadVulnerability, passedReadVulnerability_2,passedImposterMode, publicLogName, moderatorLogName):
    #descriptions of these variables can be seen in the config file
    global readVulnerability, readVulnerability_2,imposterMode, logName, mLogName
    readVulnerability = int(passedReadVulnerability)
    readVulnerability_2 = int(passedReadVulnerability_2)
    imposterMode = int(passedImposterMode)
    logName = publicLogName
    mLogName = moderatorLogName


#returns all elements in y that are not in x
def complement(x, y):
    z = {}
    for element in y.keys():
        if element not in x.keys(): z[element] = y[element]
    return z

#resets all variables
def skip():
    global currentTime, deathspeech, deadGuy, voters, targets
    currentTime = 0
    deathspeech = 0
    deadGuy = ""
    voters = {}
    targets = {}

def sleep(duration):
    global currentTime
    currentTime = time.time()
    while time.time() < currentTime + duration:
        time.sleep(1)

def setLogChat(n):
    global logChat
    logChat = n

def obscure():
    pass
    #while 1:
        #os.system('ls '+pipeRoot+'* > /dev/null 2> /dev/null')
        #time.sleep(.1)

def allow(players):
    global allowed
    allowed = players

isHandlingConnections = 1
def handleConnections(timeTillStart, randomize):
    global isHandlingConnections, all

    f = open('names.txt', 'r').read().split('\n')[0: - 1]
    if randomize: random.shuffle(f)

    for conn in range(size):
        if randomize: name = f[conn]
        else: name = 'player{}'.format(conn)
            
        if conn == rank:
            print('{} connected'.format(name))
            send('connect', dest=0)
            break
            
        t=Thread(target = connect,args = [str(conn), str(name)])
        t.setDaemon(True)
        t.start()

    sleep(int(timeTillStart))
    isHandlingConnections = 0
    all = conns
    return conns


# Modified connect function to use MPI
def connect(num, name):
    #global isHandlingConnections

    inPipe = '%stos'%num
    outPipe = 'sto%s'%num
    duration = .1

    connected = False
    connInput = ''
    try:
        while not connected:#connInput!='connect':
            
            if rank == int(num):
                send('connect', 0)
                
            comm.Barrier()
            
            if rank == 0:
                
                connInput = recv()
                
            connected = comm.bcast(1 if connInput == 'connect' and isHandlingConnections else 0, root=0)
            
            if connected:
                if rank == 0:
                    log('%s connected' % name, 1, 0, 1)
                    send('Hello, %s.  You are connected.  Please wait for the game to start.' % name, int(num))
            
            comm.Barrier()
            
            if not isHandlingConnections:
                if rank == 0:
                    send('Game already started.  Please wait for next game.', int(num))
                    send('close', int(num))
                return

            time.sleep(duration)
    except:
        pass


# Broadcast message using MPI.send() to all players with the correct rank
def broadcast(msg, players):
    global logChat
    log(msg, 1, logChat, 1)

    time.sleep(.1)
    
    for player in players:
        if player != rank:
            send(msg, dest=player)

# Send messages using MPI.send()
def send(msg, dest):
    comm.send(msg, dest=dest)
    
# Receieve any message from another MPI source
def recv():
    return comm.recv(source=MPI.ANY_SOURCE)


#print, publicLog, modLog
def log(msg, printBool, publicLogBool, moderatorLogBool):
    global logName, mLogName

    if printBool:
        print msg

    msg = '(%s) - %s\n'%(str(int(time.time())), msg)
    if publicLogBool:
        f = open(logName, 'a')
        f.write(msg)
        f.close()
    if moderatorLogBool:
        g = open(mLogName, 'a')
        g.write(msg)
        g.close()

def clear(pipes):
    for p in pipes:
        for i in range(10):
            t=Thread(target = recv, args = [p])
            t.setDaemon(True)
            t.start()

deathspeech = 0
deadGuy = ""
def multiRecv(player, players):
    global allowed, voters, targets, deathspeech, deadGuy, all

    while True:
        msg = recv()
        
        if msg is None:
            continue

        #if someones giving a deathspeech
        if deathspeech and player == deadGuy:
            broadcast('%s-%s'%(player, msg[2]), modPlayers(player, all))

        #if were voting
        elif votetime and player in voters.keys():
            vote(player, msg[2])

        #if its group chat
        elif player in allowed:
            broadcast('%s-%s'%(player, msg[2]), modPlayers(player, allowed))

        #otherwise prevent spam
        else:
            time.sleep(1)

def groupChat(players):
    for player in players.keys():
        newPlayers = modPlayers(player, players)
        t=Thread(target = multiRecv, args = [player, newPlayers])
        t.setDaemon(True)
        t.start()

#remove one pipe from pipes
def modPlayers(player, players):
    newPlayers = {}
    for p in players.keys():
        if p != player:
            newPlayers[p] = players[p]
    return newPlayers

#voteAllowDict is a dictionary of booleans that forces only one group to vote at a time.
votetime = 0
voteAllowDict = {'w':0, 'W':0, 't':0}
votes = {}
votesReceived = 0
voters = {}
targets = []
character = ""

# Global dictionary to determine if user has voted
voter_targets = {}

def poll(passedVoters, duration, passedValidTargets, passedCharacter, everyone, isUnanimous, passedIsSilent):
    global votes, voteAllowDict, allowed, votesReceived, logChat, votetime, voters, targets, character, isSilent, voter_targets

    votetime = 1
    voters = passedVoters
    votesReceived = 0
    votes = {}
    targets = passedValidTargets
    character = passedCharacter
    isSilent = passedIsSilent

    voter_targets = {}

    sleep(duration + 1)
    log(str(votes), 1, logChat, 1)

    results = []
    mode = 0
    for v in votes.keys():
        if votes[v] > mode:
            mode = votes[v]
            results = [v]
        elif votes[v] == mode:
            results.append(v)

    #this var signifies the class of result
    #0 - results[0]=victim; 1 - vote not unan; 2 - vote is tie
    resultType = 0

    if int(isUnanimous) and mode != len(passedVoters): #the voteCount of the winner is not equal the number of voters
        resultType = 1
    elif len(results) > 1 or len(results) == 0:#tie or nonvote
        resultType = 2

    validTargets = []
    votetime = 0
    voters = {}
    #voter_targets = {}

    return results, resultType

def vote(voter, target):
    global votes, votesReceived, voters, character, isSilent, voter_targets

    # Code Updated on 7/20 by Tim
    if voter_targets.get(voter, None) == None:  # Added line

        if target in targets:
            try: votes[target] += 1  # changed from += 1 to just 1
            except: votes[target] = 1
            #message[0] is sent to who[0]; message[1] sent to who[1]; etc.
            messages = []
            who = []

            log(voter + " voted for " + target, 1, 0, 1)

            if character == "witch":
                messages.append("Witch voted")
                who.append(all)
            elif character == "wolf":
                if isSilent: messages.append('%s voted.'%voter)
                else: messages.append('%s voted for %s'%(voter, target))
                #messages.append("Wolf vote received.")
                who.append(voters)

                messages.append("Wolf vote received.")
                comp = complement(voters, all)
                who.append(comp)
                #who.append(complement(voters,all))
            else:#townsperson vote
                if isSilent: messages.append('%s voted.'%voter)
                else: messages.append('%s voted for %s'%(voter, target))
                who.append(all)

            for i in range(len(messages)):
                broadcast(messages[i], who[i])


            votesReceived += 1
            voter_targets[voter] = target  

            if votesReceived == len(voters): skip()

        else:
            #vote_targets[voter] = None  # Added by Tim
            send('invalid vote: %s'%target, voters[voter][1])

    # Added by Tim    
    else:
        send('You already voted: %s'%target, voters[voter][1])

def spawnDeathSpeech(player, endtime):
    global deathspeech, deadGuy
    deathspeech = 1
    deadGuy = player

    sleep(endtime)

    deathspeech = 0
    deadGuy = ""

