#!/usr/bin/bash

#
# awscli2
#
# https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html
#

apt-get update
apt-get upgrade -y
apt-get install cmake gdb python3-pip unzip -y
wget https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -P /tmp/
unzip /tmp/awscli-exe-linux-x86_64.zip -d /tmp
/tmp/aws/install

#
# zeek
#
#  https://github.com/zeek/zeek/wiki/Binary-Packages
#

DEBIAN_FRONTEND=noninteractive apt-get install postfix -y
echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_20.04/ /' | sudo tee /etc/apt/sources.list.d/security:zeek.list
curl -fsSL https://download.opensuse.org/repositories/security:zeek/xUbuntu_20.04/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null
sudo apt update
sudo apt install zeek-lts -y

#
# suricata
#
# https://suricata.readthedocs.io/en/suricata-6.0.0/install.html#ubuntu
#

sudo add-apt-repository ppa:oisf/suricata-stable -y
sudo apt-get update
sudo apt-get install suricata -y

#
# zeek af_packet plugin
#
# https://github.com/J-Gras/zeek-af_packet-plugin
#

cd /tmp && git clone https://github.com/J-Gras/zeek-af_packet-plugin.git
cd /tmp/zeek-af_packet-plugin && export PATH=/opt/zeek/bin:$PATH && ./configure && make && make install
/opt/zeek/bin/zeek -NN Zeek::AF_Packet

#
# python3 configuration
#

pip3 install boto3
wget https://github.com/4n6ir/siphon-config/releases/download/v0.0.1-python/siphon-config.py -P /tmp/
/usr/bin/python3 /tmp/siphon-config.py

