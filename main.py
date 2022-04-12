from scp import SCPClient
from threading import Lock, Thread

import base64
import binascii
import paramiko
import csv
import io
import os
import sys
import time
import traceback
from xml.dom import minidom

USER = 'ig'
PASSWORD = '123456'
NUM_THREADS = 8
list_lock = Lock()
write_lock = Lock()


# This function helps to process SSH command and resuts the stdout content
def execute_command(ssh, command):
    (stdin, stdout, stderr) = ssh.exec_command(command)
    return [line.strip() for line in stdout.readlines()], [line.strip() for line in stderr.readlines()]


# This method handles connection to the single host
def handle_host(host):
    # Init connection
    ssh = paramiko.SSHClient()
    try:
        # Init SSH
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=USER, password=PASSWORD)
        transport = ssh.get_transport()
        channel = transport.open_session()
        channel.setblocking(1)
        channel.settimeout(30)


        pos_databases = [
            "main_ppg_be.db", "main_coloris_gamma_nl.db", "main_akzo_nl.db",
            "main_ppg_nl.db", "main_coloris_gamma_be.db", "main_akzo_be.db"
        ]
        dir_content = (execute_command(ssh, "echo 123456 | sudo -S sh -c 'ls /home/ig/Deso/redlike/server/db/'"))[0]

        if (("main_coloris_gamma_nl.db" and "main_akzo_nl.db") in dir_content) and ("main_ppg_be.db" not in dir_content):
            #Akzo
            print("Akzo")
        else:
            #PPG
            print("PPG")


    except Exception as e:
        print(e)

    finally:
        ssh.close()
        del ssh




# Thread processing method
def process_addresses(lst, num_items, list_lock, write_lock):
    while True:
        # Get the item from list of IP addresses
        with list_lock:
            if not lst:
                break
            i, host = lst.pop(0)
        # Send commands to the host
        try:
            # Try to connect 3 times and then raise an error
            for j in range(3):
                try:
                    handle_host(host)
                    break
                except:
                    if j < 2:
                        time.sleep(5.0)
                        continue
                    raise
            with write_lock:
                print
                '%04d / %04d => OK:      %s' % (i, num_items, host,)
        except Exception as e:
            with write_lock:
                print
                '%04d / %04d => FAILURE: %s ---- %s' % (i, num_items, host, e,)


# Check arguments
if len(sys.argv) < 2:
    print
    'App has to be started with text file containing IP addresses and path to image to be shown'
    sys.exit(1)
# Check file exists
ip_file_path = sys.argv[1]
if not os.path.isfile(ip_file_path):
    print
    'Definition file does not exist'
    sys.exit(1)
# Load the IP addresses
ip_addresses = [(i, address) for i, address in enumerate(open(ip_file_path, 'r').read().split(r','), start=1)]

# Create and start threads
threads = [Thread(target=process_addresses, args=(ip_addresses, len(ip_addresses), list_lock, write_lock)) for i in
           range(NUM_THREADS)]
for t in threads:
    t.start()
# Wait until they are processed
for t in threads:
    t.join()