#!/bin/bash

# Disable the gadget
cd cfg/usb_gadget/g1
echo "" > UDC

# Stop the MTP responder
killall umtprd

# Remove the MTP responder config
rm -rf /etc/umtprd/

# Remove functions from the configuration
rm configs/c.1/ffs.mtp

# Remove the strings directories in configurations
rmdir configs/c.1/strings/0x409

# Remove the configurations
rmdir configs/c.1

# Remove the functions
rmdir functions/ffs.mtp

# Remove the strings directories in the gadget
rmdir strings/0x409

# Delete the gadget
cd ..
rmdir g1

# Remove the configfg directory
cd ../../
umount cfg
rmdir cfg

# Remove the FunctionFS directory
umount /dev/ffs-mtp
rmdir /dev/ffs-mtp

# Unload the drivers
modprobe -r usb_f_fs
modprobe -r libcomposite
