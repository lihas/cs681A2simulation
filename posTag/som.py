#!/usr/bin/python3
fp = open("file2.txt")
lines = fp.readlines()
tags = {}
for line in lines:
	tag = line.split("_")	
	tags[tag[1]] =1
import pdb;pdb.set_trace()
	
	
