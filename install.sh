#!/bin/bash

sudo cp journalert.service /etc/systemd/system/
sudo mkdir /etc/journalert/
sudo cp ./* /etc/journalert/
