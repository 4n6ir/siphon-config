#!/usr/bin/python3

import boto3
import json
import os
import socket
import requests
import yaml

### LIST MONITORING INTERFACES ###

inet = []
socks = socket.if_nameindex()
for sock in socks:
    if sock[1] != 'ens5' and sock[1] != 'lo':
        inet.append(sock[1])

### ZEEK CONFIGURATION ###

os.system('cp /opt/zeek/etc/node.cfg /opt/zeek/etc/node.cfg.bkp')

f = open('/opt/zeek/etc/node.cfg','w')

f.write('[logger]\n')
f.write('type=logger\n')
f.write('host=localhost\n\n')
f.write('[manager]\n')
f.write('type=manager\n')
f.write('host=localhost\n\n')
f.write('[proxy-1]\n')
f.write('type=proxy\n')
f.write('host=localhost\n\n')

for net in inet:
    f.write('[worker-'+net[3:]+']\n')
    f.write('type=worker\n')
    f.write('host=localhost\n')
    f.write('interface=af_packet::ens'+net[3:]+'\n\n')

f.close()

os.system('/opt/zeek/bin/zeekctl install')
os.system('/opt/zeek/bin/zeekctl start')

### SURICATA CONFIGURATION ###

os.system('cp /etc/suricata/suricata.yaml /etc/suricata/suricata.yaml.bkp')

stream = open('/etc/suricata/suricata.yaml', 'r')
data = yaml.load(stream, Loader=yaml.FullLoader)

cluster = 99
count = 0
for net in inet:
    data['af-packet'][count]['interface'] = net
    data['af-packet'][count]['cluster-id'] = cluster
    data['af-packet'][count]['cluster-type'] = 'cluster_flow'
    data['af-packet'][count]['defrag'] = True
    cluster -= 1
    count += 1

with open('/etc/suricata/suricata.yaml', 'w') as yaml_file:
    yaml_file.write('%YAML 1.1\n')
    yaml_file.write('---\n\n')
    yaml_file.write(yaml.dump(data, default_flow_style=False))

os.system('suricata-update')
os.system('systemctl start suricata')
os.system('systemctl enable suricata')

### S3 BUCKET NAME ###

r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
instance = r.text

r = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document')
j = json.loads(r.text)
region = j['region']

client = boto3.client('ec2', region_name=region)

response = client.describe_instances(
    InstanceIds=[
        instance
    ]
)

vpc = response['Reservations'][0]['Instances'][0]['VpcId']

parameter = boto3.client('ssm', region_name=region)
response = parameter.get_parameter(Name='/siphon/'+vpc+'/bucket')
bucket = response['Parameter']['Value']

os.system('touch /root/'+bucket)

### SETUP CRONTAB ###

os.system('cp /etc/crontab /etc/crontab.bkp')

f = open('/etc/crontab','a')
f.write('*/5 * * * * root /opt/zeek/bin/zeekctl cron\n')
f.write('*/15 * * * * root /usr/local/bin/aws s3 sync /opt/zeek/logs s3://'+bucket+'/`hostname` --exclude "*" --include "*.log.gz"\n')
f.write('0 11 * * * root /usr/bin/suricata-update\n')
f.write('15 11 * * * root /usr/bin/systemctl restart suricata\n')
f.write('0 * * * * root /usr/bin/find /opt/zeek/logs/* -mtime +7 -type f -name "*.log.gz" -delete\n')
f.write('#')
f.close()

os.system('systemctl restart cron')
os.system('systemctl restart suricata')
