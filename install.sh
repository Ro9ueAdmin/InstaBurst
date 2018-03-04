#!/usr/bin/env bash

# configure the repository file
echo "deb http://http.kali.org/kali kali-rolling main contrib non-free" > /etc/apt/sources.list

# install Tor && requirements
apt-get update && apt-get install tor -y && apt autoremove -y
pip install -UI -r requirements.txt

