import socket
import os


#starting a connection    
TCP_IP = '127.0.0.1'    #add the IP of vRLI
TCP_PORT = 123          #add the port 514
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))


#imp vars
temp=""
new_record = ""
counter_start = 0
counter_end = 0

#make a temp file if not created before
try:
    ft = open('/var/log/nsx-idps/temp.txt','x')
    ft.close()
except:
    pass

#get the pointer string
ft = open('/var/log/nsx-idps/temp.txt','r')
tempList = ft.readlines()
if len(tempList) != 0:
    temp = tempList[0]
    if temp[-2:]!="}}":
        new_record = temp
ft.close()


#the host machine name
machine_name = (socket.gethostname())+" "



#read the log file
fr = open('/var/log/nsx-idps/nsx-idps-events.log','r')             #change the file name to log file name
contents  = fr.readlines()
fr.close()
    
#initial var and confirm start pointer positions
counter_end = len(contents)
    
if len(contents)<counter_start:
    flag = 0
    for i in range(len(contents)-1,-1,-1):
        if contents[i].strip() == temp:
            counter_start = i+1
            flag = 1
            break
    if flag == 0:
        counter_start = 0
else:
    if temp != "":
        if contents[counter_start-1].strip() != temp:
            flag = 0
            if counter_start == 0:
                counter_start = len(contents)
            for i in range(counter_start-1,-1,-1):
                if contents[i].strip() == temp:
                    counter_start = i+1
                    flag = 1
                    break
            if flag == 0:
                counter_start = 0
        else:
            counter_start = len(contents)
    else:
        counter_start = 0

#stitching      
if counter_end>counter_start:
    split_record = "IDPS_EVT: ["
        
    for record in contents[counter_start:counter_end]:
        if record[21:32] == split_record:
            if new_record != "":
                MESSAGE = bytes(new_record, 'utf-8')
                s.send(MESSAGE)                  
                new_record = ""
            new_record = (record).strip()
            new_record = new_record[:21]+machine_name+new_record[21:]
        else:
            new_record += (record[31:]).strip()
    if new_record[-2:]=="}}" or new_record[-3:-1]=="}}":
        MESSAGE = bytes(new_record, 'utf-8')
        s.send(MESSAGE)                
        new_record = ""
    counter_start = counter_end
    temp = contents[-1].strip()
    fw = open('/var/log/nsx-idps/temp.txt','w')
    fw.write(temp)
    fw.close()

#closing the connection
s.close()
