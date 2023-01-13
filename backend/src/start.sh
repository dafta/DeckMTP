#!/bin/sh

# Get the serial number
export SERIAL_NUMBER=$(dmidecode -s system-serial-number)

# Load the drivers
modprobe libcomposite

# Create the configfs directory
mkdir cfg
mount none cfg -t configfs

# Create the gadget
mkdir cfg/usb_gadget/g1
cd cfg/usb_gadget/g1

# Specify the vendor and product ID
echo 0x3000 > idProduct
echo 0x28DE > idVendor

# Create the gadget configuration
mkdir configs/c.1

# Create the strings directories
mkdir strings/0x409
mkdir configs/c.1/strings/0x409

# Specify the serial number, manufacturer, and product strings
echo "$SERIAL_NUMBER" > strings/0x409/serialnumber
echo "Valve" > strings/0x409/manufacturer
echo "Steam Deck" > strings/0x409/product

# Set the configuration
echo "Conf 1" > configs/c.1/strings/0x409/configuration
echo 120 > configs/c.1/MaxPower

# Create the gadget function
mkdir functions/ffs.mtp

# Associate the MTP function with it's configuration
ln -s functions/ffs.mtp configs/c.1

# Create the FunctionFS directory
mkdir /dev/ffs-mtp
mount -t functionfs mtp /dev/ffs-mtp

cd ../../..

# Copy the MTP responder config to /etc/umtprd
mkdir /etc/umtprd
cp ./umtprd.conf /etc/umtprd/

# Replace the serial number in the MTP responder config
sed -i -e "s/SERIAL_NUMBER/$SERIAL_NUMBER/" /etc/umtprd/umtprd.conf

# Start the MTP responder
./umtprd &

# Add the SD card if it's mounted
if [[ -d "/run/media/mmcblk0p1" ]]; then
	./umtprd '-cmd:addstorage:/run/media/mmcblk0p1 "SD Card" rw'
fi

sleep 1

# Enable the USB gadget
ls /sys/class/udc/ > cfg/usb_gadget/g1/UDC
