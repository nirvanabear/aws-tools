import boto3
import time
import sys
# import json
# import datetime
# import pprint


# Required for processing AWS output as JSON

# def datetime_handler(x):
#     if isinstance(x, datetime.datetime):
#         return x.isoformat()
#     raise TypeError("Unknown type")
    

#————————————————————————————#


# Pending: 0, Running: 16, Stopped: 80, Stopping: 64

def spinny_things(counter):
    wait_icon = ['—', '\\', '|', '/', '—', '\\', '|', '/']
    return "  " + wait_icon[counter % 8] + wait_icon[(counter + 1) % 8] + wait_icon[(counter + 2) % 8] + wait_icon[(counter + 3) % 8] + wait_icon[(counter + 4) % 8]


def check_state(instance_id):
    client = boto3.client('ec2')
    instance_data = client.describe_instances(InstanceIds=[instance_id])
    state = instance_data['Reservations'][0]['Instances'][0]['State']['Code']
    print("instance state: " + instance_data['Reservations'][0]['Instances'][0]['State']['Name'])
    return [client, state]


def start_ec2(client, instance_id, state):
    start_instance = input("Want to start the instance? (y/n) ")
    if start_instance == 'y' or start_instance == 'Y':
        start_data = client.start_instances(InstanceIds=[instance_id])
        state = start_data['StartingInstances'][0]['CurrentState']['Code']
        print(start_data['StartingInstances'][0]['CurrentState']['Name'])
        # pprint.pprint(start_data)

    return [state, start_instance]


def stop_ec2(client, instance_id, state, icon_counter):
    stop_instance = input("Want to stop the instance? (y/n) ")
    if stop_instance == 'y' or stop_instance == 'Y':
        stop_data = client.stop_instances(InstanceIds=[instance_id])
        print(stop_data['StoppingInstances'][0]['CurrentState']['Name'])

        while state != 80:
            instance_data = client.describe_instances(InstanceIds=[instance_id])
            state = instance_data['Reservations'][0]['Instances'][0]['State']['Code']
            print(spinny_things(icon_counter), end='\r')
            sys.stdout.flush()
            icon_counter += 1

        print(instance_data['Reservations'][0]['Instances'][0]['State']['Name'])
    #     sys.exit()
    # else:
    #     sys.exit()
    return state


def find_public_dns(client, instance_id, state, icon_counter):
    public_dns_name = ''
    # print("loading")

    ## TODO ## Could use a timeout to keep this from getting stuck.
    while not public_dns_name and (state == 16 or state == 0):
        instance_data = client.describe_instances(InstanceIds=[instance_id])
        # print(json.dumps(instance_data, sort_keys=True, indent=4, default=datetime_handler))
        public_dns_name = instance_data['Reservations'][0]['Instances'][0]['PublicDnsName']
        print(spinny_things(icon_counter), end='\r')
        sys.stdout.flush()
        icon_counter += 1

    print("\npublic DNS: " + public_dns_name)
    return public_dns_name


## TODO ## Bottom of the config file is a mess.
def update_config(public_dns_name, config_dir, config_entry):
    with open(config_dir, 'r+') as file:
        data = file.readlines()

        for j in range(len(data)):
            if data[j].find(config_entry) != -1:
                data[j+2] = "    HostName " + public_dns_name + "\n"

    with open(config_dir, 'w') as file:
        # file.seek(0)
        file.writelines(data)



