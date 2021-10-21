#!/bin/bash

# RUN ME AS ROOT!

if [[ $(whoami) != "root" ]]; then
	echo "Please, run me as root"
	exit 1
fi

if [[ $# -ne 4 ]]; then
	echo "Installation run format:"
	echo "bash mcafee-collector-install.sh <API user> <API password> <API client_id> <file log or not {-y, -n}>"
	exit 1
fi

user=$1
password=$2
client_id=$3
file_log=$4

if [[ $file_log != "-y" ]] && [[ $file_log != "-n" ]]; then
	echo "Last option should be -y or -n."
	exit 1
fi

# Setup options based on OS distribution
if [[ $(cat /etc/os-release | grep CentOS | wc -l) -gt 0 ]]; then
	PM=yum
	SERVICE_ROOT=/usr/lib/systemd/system/
elif [[ $(cat /etc/os-release | grep Ubuntu | wc -l) -gt 0 ]]; then
	PM=apt
	apt update -y
	SERVICE_ROOT=/lib/systemd/system/
fi

# Install Python 3 and non-native libraries
$PM install -y python3 python3-pip
python3 -m pip install requests python-dateutil

# Create folders
mkdir -p /opt/mcafee-collector/conf
mkdir -p /opt/mcafee-collector/bin
mkdir -p /var/log/mcafee-collector
# And move files to them
cp bin/main.py /opt/mcafee-collector/bin
cp installation/mcafee-collector.service $SERVICE_ROOT
cp libs/* /opt/mcafee-collector/bin

# Configure API credentials
cat <<EOF > /opt/mcafee-collector/conf/properties.conf
MCAFEE_USER=$user
MCAFEE_PASSWORD=$password
MCAFEE_CLIENT_ID=$client_id
EOF
if [[ $file_log == "-y" ]]; then
	echo "LOG_FILE_OPT=" >> /opt/mcafee-collector/conf/properties.conf
chmod 700 /opt/mcafee-collector/conf/properties.conf

# Enable and start service
systemctl daemon-reload
systemctl enable mcafee-collector
systemctl restart mcafee-collector

if [[ $(systemctl is-active mcafee-collector) == "active" ]]; then
	echo "Installation completed successfully"
	exit 0
else
	echo "Installation failed. Please, review parameters and service logs 'journalctl -xeu mcafee-collector'"
	exit 1
fi