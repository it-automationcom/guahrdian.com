#!/usr/bin/python3

import osm
import dgm
import pbf
import os
import sys

returncode=0
def check(name,expected,got):
    print("\033[4;30;37m",name,"\033[0;0m")
    print("Expected:",expected)
    print("Got:", got)
    if expected == got:
        print("\033[1;30;42m Passed \033[0;0m", flush=True)
        sys.stdout.flush()
    else:
        print("\033[1;30;41m Failed \033[0;0m", flush=True)
        global returncode
        returncode=1

def result(returncode):
    if returncode==0:
        print("\033[4;30;37m Overall Result: \033[0;0m")
        print("\033[1;30;42m Passed \033[0;0m", flush=True)
        return(0)
    else:
        print("\033[4;30;37m Overall Result: \033[0;0m")
        print("\033[1;30;41m Failed \033[0;0m", flush=True)
        return(1)

dreisbach=pbf.trace(3309646)
check("Ways",244793623,dreisbach.get_ways()[0])
check("Nodes",2520664689,dreisbach.get_nodes()[0])
check("Points",50.4341620,dreisbach.get_points()[0][0])
result(returncode)
