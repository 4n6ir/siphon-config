# siphon-config
A two-stage configuration script to install and configure a stand-alone packet capture sensor for network security monitoring. 
### SOFTWARE
- af_packet - https://github.com/J-Gras/zeek-af_packet-plugin
- awscliv2 - https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html
- suricata - https://suricata.readthedocs.io/en/suricata-6.0.0/install.html#ubuntu
- zeek - https://github.com/zeek/zeek/wiki/Binary-Packages
### CONFIGURATION
The af_packet interface is a device-level packet socket that scales processing across threads to form a fanout group through the Suricata and Zeek configuration files.
- /etc/suricata/suricata.yaml
- /opt/zeek/etc/node.cfg
### S3 BUCKET ARCHIVE
AWS CLI version 2 is used to sync compressed log files from the local EBS volume to the S3 bucket every 15 minutes.
### DISK CLEANUP
Unix commands are executed every hour to keep only 7 days of logs available on the local EC2 instance.
### IDS UPDATES
ET OPEN rulesets are updated every day at 11 AM UTC.
