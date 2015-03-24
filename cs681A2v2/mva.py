R=0.0
S=1.0
Q=0.0
T=6.0 #THINK TIME
TP=0.0
M=1000 #NUMBER OF USERS
for i in range(0,M):
	R=S*(1+Q)
	TP=(i+1)/(R+T)
	Q=R*TP
	
	print "response time ",R,"Queue length",Q,"Throughput",TP
