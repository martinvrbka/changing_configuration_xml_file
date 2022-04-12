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


with open("configuration.xml", "w") as fp:
    pass
xml_path = os.path.dirname(os.path.realpath(__file__)) + "\configuration.xml"
print(xml_path)

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

        # Init SCP
        scp = SCPClient(transport)
        print "init ok"
        # Read machine config
        scp.get('/usr/lib/evodriver/bin/EVOlocal/config/configuration.xml', xml_path)
        print "data read"
        doc = minidom.parse(xml_path)
        print "data parsed"

        # Parse file
        dispensers = doc.getElementsByTagName('DISPENSER')

        # In case it's frontdesk, there is nothing to do
        if len(dispensers) == 0:
            raise ValueError('Invalid dispenser file')

        pos_databases = [
            "main_ppg_be.db", "main_coloris_gamma_nl.db", "main_akzo_nl.db",
            "main_ppg_nl.db", "main_coloris_gamma_be.db", "main_akzo_be.db"
        ]
        dir_content = (execute_command(ssh, "echo 123456 | sudo -S sh -c 'ls /home/ig/Deso/redlike/server/db/'"))[0]

        if (("main_coloris_gamma_nl.db" and "main_akzo_nl.db") in dir_content) and ("main_ppg_be.db" not in dir_content):
            #Akzo
            with open(xml_path, "w") as f:

                for colorant in doc.getElementsByTagName('COLORANT'):
                    for canister in colorant.getElementsByTagName('CANISTER'):
                        if canister.attributes['max_q'].value == "1500":
                            canister.attributes['res_w'].value = "400.0000"
                            canister.attributes['res_q'].value = "300.0000"
                        for circuit in canister.getElementsByTagName('CIRCUIT'):
                            for motors in circuit.getElementsByTagName('MOTORS'):
                                for motor in motors.getElementsByTagName('MOTOR'):
                                    try:
                                        motor.attributes['pause'].value = "5400"
                                        motor.attributes['activity'].value = "60"
                                    except Exception as e:
                                        print e
                f.write(doc.toxml())
        else:
            #PPG
            with open(xml_path, "w") as f:

                for colorant in doc.getElementsByTagName('COLORANT'):
                    colorants_to_change = ["W-83", "W-73", "W-72", "W-84"]
                    if colorant.attributes['code'].value in colorants_to_change:
                        for canister in colorant.getElementsByTagName('CANISTER'):
                            for circuit in canister.getElementsByTagName('CIRCUIT'):
                                for motors in circuit.getElementsByTagName('MOTORS'):
                                    for motor in motors.getElementsByTagName('MOTOR'):
                                        try:
                                            motor.attributes['policy'].value = "0"
                                        except Exception as e:
                                            print e
                f.write(doc.toxml())


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