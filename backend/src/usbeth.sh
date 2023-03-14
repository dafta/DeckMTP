#!/bin/sh

if [ "$UID" -ne 0 ]; then
	echo "This script needs to be executed as root"
	exit 1
fi

vendor_id="0x3000" # Valve
product_id="0x28DE"
serial_number="$(dmidecode -s system-serial-number)" # The Steam Deck's serial number
manufacturer="Valve" # Manufacturer
product="Steam Deck" # Product
device="0x1004" # Device version
usb_version="0x0200" # USB 2.0
device_class="2" # Communications
cfg1="CDC" # Config 1 description
cfg2="RNDIS" # Config 2 description
power=250 # Max power
dev_mac1="42:61:64:55:53:42"
host_mac1="48:6f:73:74:50:43"
dev_mac2="42:61:64:55:53:44"
host_mac2="48:6f:73:74:50:45"
ms_vendor_code="0xcd" # Microsoft
ms_qw_sign="MSFT100" # Microsoft
ms_compat_id="RNDIS" # Matches Windows RNDIS drivers
ms_subcompat_id="5162001" # Matches Windows RNDIS 6.0 driver

cdc_mode="ecm" # Which CDC gadget to use
start_rndis=true # Whether to start the Microsoft RNDIS gadget

while getopts "ncerR" option ${@:2}; do
	case "${option}" in
		"n")
			cdc_mode=ncm
			;;
		"c")
			cdc_mode=ecm
			;;
		"e")
			cdc_mode=eem
			;;
		"r")
			start_rndis=true
			;;
		"R")
			start_rndis=false
			;;
	esac
done

case "$1" in
	start)
		# Create the networkd config file for the USB interface
		cat << EOF > /etc/systemd/network/usb0.network
[Match]
Name=usb0

[Network]
Address=192.168.100.1/24
DHCPServer=true
IPMasquerade=ipv4

[DHCPServer]
PoolOffset=100
PoolSize=20
EmitDNS=yes
DNS=8.8.8.8
EOF

		cat << EOF > /etc/systemd/network/usb1.network
[Match]
Name=usb1

[Network]
Address=192.168.101.1/24
DHCPServer=true
IPMasquerade=ipv4

[DHCPServer]
PoolOffset=100
PoolSize=20
EmitDNS=yes
DNS=8.8.8.8
EOF

		# Start networkd
		systemctl start systemd-networkd

		# Load the drivers
		modprobe libcomposite

		# Create the gadget
		mkdir /sys/kernel/config/usb_gadget/g.1
		cd /sys/kernel/config/usb_gadget/g.1

		# Specify the vendor and product ID
		echo "${vendor_id}" > idVendor
		echo "${product_id}" > idProduct

		# Create the gadget configuration
		mkdir configs/c.1

		# Create the strings directories
		mkdir strings/0x409
		mkdir configs/c.1/strings/0x409

		# Specify the serial number, manufacturer, and product strings
		echo "${serial_number}" > strings/0x409/serialnumber
		echo "${manufacturer}" > strings/0x409/manufacturer
		echo "${product}" > strings/0x409/product

		# Specify the device version, USB specification, and device class
		echo "${device}" > bcdDevice
		echo "${usb_version}" > bcdUSB
		echo "${device_class}" > bDeviceClass

		# Set the configuration description and power
		echo "${cfg1}" > configs/c.1/strings/0x409/configuration
		echo "${power}" > configs/c.1/MaxPower

		# Create the gadget function
		mkdir functions/${cdc_mode}.0

		# Set the MAC addresses of the gadget
		echo "${host_mac1}" > functions/${cdc_mode}.0/host_addr
		echo "${dev_mac1}" > functions/${cdc_mode}.0/dev_addr

		# Start RNDIS if enabled
		if [ "${start_rndis}" = true ]; then
			# Create the gadget configuration
			mkdir configs/c.2

			# Create the strings directories
			mkdir configs/c.2/strings/0x409

			# Specify the configuration description and power
			echo "${cfg2}" > configs/c.2/strings/0x409/configuration
			echo "${power}" > configs/c.2/MaxPower

			# Set some Microsoft specific configuration
			echo "1" > os_desc/use
			echo "${ms_vendor_code}" > os_desc/b_vendor_code
			echo "${ms_qw_sign}" > os_desc/qw_sign

			# Create the gadget function
			mkdir functions/rndis.0

			# Set the MAC addresses of the gadget
			echo "${host_mac2}" > functions/rndis.0/host_addr
			echo "${dev_mac2}" > functions/rndis.0/dev_addr

			# Set the RNDIS driver version
			echo "${ms_compat_id}" > functions/rndis.0/os_desc/interface.rndis/compatible_id
			echo "${ms_subcompat_id}" > functions/rndis.0/os_desc/interface.rndis/sub_compatible_id
		fi

		# Associate the CDC function with its configuration
		ln -s functions/${cdc_mode}.0 configs/c.1/

		# Associate the RNDIS function with its configuration
		if [ "${start_rndis}" = true ]; then
			ln -s functions/rndis.0 configs/c.2
			ln -s configs/c.2 os_desc
		fi

		# Enable the gadget
		ls /sys/class/udc > UDC
		;;

	stop)
		# Disable the gadget
		cd /sys/kernel/config/usb_gadget/g.1
		echo "" > UDC

		# Remove functions from the configuration
		rm configs/c.1/ncm.0 2> /dev/null
		rm configs/c.1/ecm.0 2> /dev/null
		rm configs/c.1/eem.0 2> /dev/null
		rm configs/c.2/rndis.0 2> /dev/null

		# Remove the strings directories in configurations
		rmdir configs/c.1/strings/0x409
		rmdir configs/c.2/strings/0x409 2> /dev/null

		# Remove the configurations
		rmdir configs/c.1
		rm os_desc/c.2 2> /dev/null
		rmdir configs/c.2 2> /dev/null

		# Remove the functions
		rmdir functions/ncm.0 2> /dev/null
		rmdir functions/ecm.0 2> /dev/null
		rmdir functions/eem.0 2> /dev/null
		rmdir functions/rndis.0 2> /dev/null

		# Remove the strings directories in the gadget
		rmdir strings/0x409

		# Delete the gadget
		cd ..
		rmdir g.1

		# Unload the drivers
		cd ../../
		modprobe -r usb_f_ncm
		modprobe -r usb_f_ecm
		modprobe -r usb_f_eem
		modprobe -r usb_f_rndis
		modprobe -r libcomposite

		# Stop networkd
		systemctl stop systemd-networkd 2> /dev/null

		# Remove the networkd config files for USB interfaces
		rm /etc/systemd/network/usb0.network
		rm /etc/systemd/network/usb1.network
		;;
	*)
		echo "Usage:"
		echo -e "\t./usb-ether.sh start\tStarts the USB ethernet"
		echo -e "\t\t-n\tUse the CDC-NCM USB Ethernet driver (for OSX and iOS)"
		echo -e "\t\t-c\tUse the CDC-ECM USB Ethernet driver (default)"
		echo -e "\t\t-e\tUse the CDC-EEM USB Ethernet driver"
		echo -e "\t\t-r\tEnable the RNDIS USB Ethernet driver for Windows (default)"
		echo -e "\t\t-R\tDisable the RNDIS USB Ethernet driver for Windows"
		echo -e "\t./usb-ether.sh stop - Stops the USB ethernet"
		;;
esac