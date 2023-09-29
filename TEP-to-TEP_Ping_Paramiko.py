import paramiko
import re
import time
import getpass
import os
import sys
import threading

start_time = time.time() #getting start time

commands = ["get interfaces | find IP/Mask", "get neighbor | find IP", "get stats"] # changing the commands here would break the script. Be sure on the changes you are making.
T_width=os.get_terminal_size().columns # extracting local machines terminal width size
T_height=os.get_terminal_size().lines # extracting local machines terminal height size
src_tep_ips = []
dst_tep_ips = []
def main():
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
    src_tep_thread = threading.Thread(target=get_src_tep,kwargs={'ssh_connection':ssh_connection})
    dst_tep_thread = threading.Thread(target=get_dst_tep,kwargs={'ssh_connection':ssh_connection})
    src_tep_thread.start()
    dst_tep_thread.start()
    src_tep_thread.join()
    dst_tep_thread.join()
    print("-------------------------\n",src_tep_ips,dst_tep_ips)
    tep_to_tep_ping(ssh_connection, src_tep_ips, dst_tep_ips)
    ssh_close(ssh_connection)
# The function will SSH into the edge host
def ssh_connect(ip, port, username, password,timeout_ssh):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, port, username, password,timeout=timeout_ssh)
        print(f"SSH connected to {ip}")
        return ssh_client # returning the ssh connection stat  ssh_connection variable
    except Exception as e:
        print(f"Exception occured: {str(e)}")

def get_src_tep(ssh_connection):
    try:
        output_buffer = ""
        ssh_shell = ssh_connection.invoke_shell(width=T_width, height=T_height) # shell invoked with local terminal screen size
        print("Shell invoke successful get_src_tep()")
        ssh_shell.send("vrf 0\n") # executing this command as the exit logic is difficult
        print("VRF 0 sent")
        #ssh_shell.recv(4096) # wait for data to receive 
        ssh_shell.send(f"{str(commands[0])}\n")
        ssh_shell.send(f"{str(commands[2])}\n") # passing to break while loop/exit from terminal once the output is sent
        while True:
            output_buffer += ssh_shell.recv(65535).decode("utf-8") #add append output from shell to output_buffer str variable 
            if "Logical Router" in output_buffer:
                print("Breaking loop as match found \"Logical Router\"")
                break
        print(output_buffer)
        src_tep_buffer = re.findall(r'(IP\/Mask       : \d+.\d+.\d+.\d+)', output_buffer) #finding all the IPs and it will also contain "IP/Mask       :"
        tep_ips = re.findall(r'(\d+.\d+.\d+.\d+)', str(src_tep_buffer)) #filtering only IP and excluding "IP/Mask"
        #print(tep_ips) #open tap to flow the data
        print("source TEP IPs are: ", tep_ips)
        global src_tep_ips 
        src_tep_ips = tep_ips # sending Source tep IPs to global variable
        return None
    except Exception as e:
        print(f"Failed to invoke shell {str(e)} ")
    finally:
        ssh_shell.close()
        print("Interactive ssh shell closed(get_src_tep)")

def get_dst_tep(ssh_connection):
    try:
        output_buffer = ""
        ssh_shell = ssh_connection.invoke_shell(width=T_width, height=T_height) # shell invoked with local terminal screen size
        print("Shell invoke successful get_dst_tep()")
        ssh_shell.send("vrf 0\n") # executing this command as the exit logic is difficult
        print("VRF 0 sent")
        #ssh_shell.recv(4096) # wait for data to receive 
        ssh_shell.send(f"{str(commands[1])}\n")
        ssh_shell.send(f"{str(commands[2])}\n") # passing to break while loop
        #ssh_shell.recv(4096)
        while True:
            output_buffer += ssh_shell.recv(65535).decode("utf-8") #add append output from shell to output_buffer str variable 
            if "Logical Router" in output_buffer:
                print("Breaking loop as match found \"Logical Router\"")
                break
        print(output_buffer)
        dst_tep_buffer = re.findall(r'(IP          : \d+.\d+.\d+.\d+)', output_buffer) #finding all the IPs and it will also contain "IP/Mask       :"
        tep_ips = re.findall(r'(\d+.\d+.\d+.\d+)', str(dst_tep_buffer)) #filtering only IP and excluding "IP/Mask"
        #print(tep_ips) #open tap to flow the data
        print("Neighbor TEP IPs are: ", tep_ips)
        uniq_dst_tep_ips = list(set(tep_ips)) # prints unique tep IPs
        print(f"The unique neighbor TEP IPs are: {uniq_dst_tep_ips} ") # Translating to set to get unique values and convert back to list to preserve the orginal order
        global dst_tep_ips 
        dst_tep_ips = uniq_dst_tep_ips # sending destination tep IPs to global variable
        return None
    except Exception as e:
        print(f"Failed to invoke shell {str(e)} ")
    finally:
        ssh_shell.close()
        print("Interactive SSH shell closed (get_dst_tep)")
def tep_to_tep_ping(ssh_connection, src_ip, dst_ip):
    try:
        output = ""
        combined_ping = []
        ssh_shell = ssh_connection.invoke_shell(width=T_width, height=T_height) # shell invoked with local terminal screen size
        print("Shell invoke successfultep_to_tep_ping()")
        ssh_shell.send("vrf 0\n") # executing this command as the exit logic is difficult
        print("VRF 0 sent")
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
        print(f"{combined_ping}") # combined_ping list has the ping commands with "\n"
        count = 0
        if len(combined_ping) != 0:
            for command in combined_ping:
                new_data = ""
                ssh_shell.send(command)
                print(f"command {command} sent")
                while True:
        #ssh_shell.send('ping 8.8.8.8 repeat 3\n')
                    new_data += ssh_shell.recv(65535).decode("utf-8")
                    if "ping statistics" in new_data:
                        time.sleep(0.3)  #sleeping to finish the complete ping output
                        count = count+1
                        break
                output += new_data  # This variable has ping output
                #print("**********------------------********** The output is ***********_________________***********\n",new_data)
            print(output)  # Printing TEP_TO_TEP ping output
            print("The count of Ping commands is :", len(combined_ping))
            print("The count of ping output is: ",count)
        else:
            print("Sorry I couldn't construct the Ping as the I didn't get the IPs")
        
    except Exception as e:
        print(f"Exception occured(tep_to_tep_pig) {str(e)}")
    finally:
        ssh_shell.close()
        print("Interactive SSH shell closed (tep_to_tep_ping)")
# The function will close the SSH of edge host
def ssh_close(ssh_connection):
    try:
        ssh_connection.close()
        print("SSH connection closed")
    except Exception as e:
        print(f"Failed to close ssh connection exception occured {str(e)} ")
if __name__ == "__main__":
    main()
print(f"Total time taken is to complete is: {time.time()-start_time} Seconds")
