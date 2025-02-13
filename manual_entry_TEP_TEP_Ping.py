from tqdm import tqdm
import paramiko
import re
import time
import getpass
import os
import sys
import threading
import logging
import datetime
#import pyfiglet

start_time = time.time() #getting start time

T_width=os.get_terminal_size().columns # extracting local machines terminal width size
T_height=os.get_terminal_size().lines # extracting local machines terminal height size
log_file = datetime.datetime.now().strftime('test_tep2tep_ping_%d%m%y_%H_%M_%S.log') #log file name to send the output to logfile from functions.
# Requirements and pre-checks function
def main():
    while True:
        try:
            edge_ip = input("Enter an Edge IP address,(no plural)\n") #enter the Edge IP, only provide 1 IP address
            username = "admin" # change the username accordingly
            delay_print="Username \"admin\" is considered as default."
            for c in delay_print:
                sys.stdout.write(c)
                sys.stdout.flush()
                time.sleep(0.03)
            print()
            #password = input("Enter the SSH password for Edge") #provide the password here
            password = getpass.getpass("Enter the SSH password for Edge\n") #hiding the password entry
            port = 22
            timeout_seconds = 120 # if you see get a Socket timeout error increase the value to the approx time required to execute the commands.
            ssh_connection = ssh_connect(edge_ip, port, username, password,timeout_seconds)
            for counter in reversed(range(5)):
                print(counter)
                time.sleep(1)
                counter -= counter
            src_tep_ips = input("Enter the Source IP address, Comma Seperated")
            dst_tep_ips = input("Enter the Destination IP address, Comma Seperated ")
            print("-------------------------\n","source TEPS: ",src_tep_ips,"\n","destination TEPS: ", dst_tep_ips)
            tep_to_tep_ping(ssh_connection, src_tep_ips, dst_tep_ips)
            ssh_close(ssh_connection)
            if input("\n\n\n\n---------> Do you want to continue? (Hit 'N' to exit) <----------\n\n\n") == 'N':
                print("\n\n\n\t\t\tGood Bye 🙋🏽‍♂️ ", "\n\n\n")
                break
        except KeyboardInterrupt:
            if ssh_connection:
                ssh_close(ssh_connection)
                break
# The function will SSH into the edge host
def ssh_connect(ip, port, username, password,timeout_ssh):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, port, username, password,timeout=timeout_ssh)
        print(f"SSH connected to {ip}")
        logging_func(f"\n\nSSH connected to {ip}\n")
        return ssh_client # returning the ssh connection stat  ssh_connection variable
    except Exception as e:
        print(f"Exception occured: {str(e)}")
        sys.exit(1)
# function to TEP-TEP ping 
def tep_to_tep_ping(ssh_connection, src_ip, dst_ip):
    try:
        output = ""
        combined_ping = []
        ssh_shell = ssh_connection.invoke_shell(width=T_width, height=T_height) # shell invoked with local terminal screen size
        print("Shell invoke successful tep_to_tep_ping()")
        ssh_shell.send("vrf 0\n") # executing this command as the exit logic is difficult
        #print("VRF 0 sent")
        ssh_shell.recv(4096) # wait for data to receive 
        #composing ping command for TEP to TEP Ping
        for destination in set(dst_ip): # converting to set to filter with unique values
            for source in set(src_ip):  # converting to set to filter with unique values
                if destination != source:  # Ensure you're not pinging the same IP
                    ping_command = f"ping {destination} source {source} repeat 3 dfbit enable size 1650" #update the repeat, dfbit , size  values according to requirement
                    final_ping_command = ping_command + "\n"
                    #print(f"Executing ping command: {ping_command}") # gives the exact ping commands to execute.
                    combined_ping.append(final_ping_command) #sending final_ping_command str to combined_ping list
        #combined_ping.append("get stats \n") # command to exit while loop (expted string is "Logical Router") 
        #print(f"{combined_ping}") #GATE # combined_ping list has the ping commands with "\n" 
        count = 0
        if len(combined_ping) != 0:
            for command in tqdm(combined_ping, colour='MAGENTA'):
                new_data = ""
                ssh_shell.send(command)
                #tqdm.write(f"sending {command} ") #Gate to print the commands getting executed currently
                while True:
        #ssh_shell.send('ping 8.8.8.8 repeat 3\n')
                    new_data += ssh_shell.recv(65535).decode("utf-8")
                    if "ping statistics" in new_data:
                        time.sleep(0.3)  #sleeping to finish the complete ping output
                        count = count+1
                        break
                output += new_data  # This variable has ping output streamed.
                #print("**********------------------********** The output is ***********_________________***********\n",new_data)
            print("\n\n\n",output)  # Printing TEP_TO_TEP ping output
            print("The count of Ping commands is :", len(combined_ping))
            print("The count of ping output is: ",count)
            print(f"Total time taken is to complete is: {time.time()-start_time} Seconds")
            logging_func(output) #sending TEP to TEP ping output to log file
            if input("Do you want to summarize the TEP-to-TEP output? (Y/N)\n") != 'N':
                summarize_TEP_ping(output)
        else:
            print("Sorry I couldn't construct the Ping as the I didn't get the IPs")
        
    except Exception as e:
        print(f"Exception occured(tep_to_tep_ping) {str(e)}")
        sys.exit(1)
    finally:
        ssh_shell.close()
        print("Interactive SSH shell closed (tep_to_tep_ping)")
# Summarizing the TEP-TEP function output below
def summarize_TEP_ping(f_cont):
    logme=''
    #print(f_cont)
    print("---------TEP_to_TEP_Ping Summary-------------------\n")
    match_header = re.findall(r'(ping \d+\.\d+\.\d+.\d+ source \d+\.\d+\.\d+.\d+ .*)', f_cont)
    #match_output = re.search(r'(\d+ packets transmitted, \d+ packets received, \d+.\d+% packet loss)', f_cont) #
    match_output = re.findall(r'(\d+) packets transmitted, (\d+) packets received, (\d+.\d+)% packet loss', f_cont)
    for i in range (len(match_output)):
        #is where you are modifying the code to send the output to logfile and also print
        #print(f"{i+1} {match_header[i]}")
        logme += f"\n{i+1} {match_header[i]}\n"
        #print(match_output[i]) #this will print whole "sent , received and loss" from ping output
        sent_pkt = int(match_output[i][0])
        received_pkt = int(match_output[i][1])
        if received_pkt > 0:
            if int(match_output[i][0]) % int(match_output[i][1]) > 0.0:
                logme += "     Alert: Packet loss found below\n"
        else:
            logme += "     Alert: No packets received\n"
        #print(f"    Sent {match_output[i][0]}, Received {match_output[i][1]}, Lost %: {match_output[i][2]} \n") #replace of this is "logme variable"
        logme += f"    Sent {match_output[i][0]}, Received {match_output[i][1]}, Lost %: {match_output[i][2]} \n"
    print(logme)
    logging_func(logme) #sending cont of log variable to logger function
#Universal Logging Function
def logging_func(log_cont):
        #logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode="a+",format="%(asctime)-15s %(levelname)-8s %(message)s")
        logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode="a+")
        logging.info(log_cont)
# The function will close the SSH of edge host
def ssh_close(ssh_connection):
    try:
        ssh_connection.close()
        print("SSH connection closed")
    except Exception as e:
        print(f"Failed to close ssh connection exception occured {str(e)} ")
if __name__ == "__main__":
    main()