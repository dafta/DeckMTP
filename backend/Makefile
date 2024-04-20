# All the systemd service files that need to be copied to output
services := umtprd.service
services += gadget-init.service
services += gadget-start.service
services += usbgadget-func-mtp.service

# All the config files that need to be copied to output
configs := gadget

# All the scripts that need to be copied to output
scripts := gadget-init.sh
scripts += gadget-start.sh

# This is the default target, which will be built when
# you invoke make
.PHONY: all
all: umtprd $(services) $(scripts) $(configs)

# This rule creates the output directories
out:
	mkdir -p out
	mkdir -p out/scripts
	mkdir -p out/configs
	mkdir -p out/services

# This rule tells make how to build the MTP responder
umtprd: out
	# Enable USB 3.0 support
	sed -i -e 's%//#define CONFIG_USB_SS_SUPPORT 1%#define CONFIG_USB_SS_SUPPORT 1%' src/uMTP-Responder/inc/buildconf.h

	# Build uMTP-Reponder
	make -C src/uMTP-Responder/

	# Copy output to output directory there
	cp src/start.sh out/scripts/
	cp src/stop.sh out/scripts/
	cp src/umtprd.conf out/configs/
	cp src/uMTP-Responder/umtprd out/

# This rule copies all the relevant systemd service files
$(services): out
	cp src/systemd-gadget/$@ out/services/

# This rule copies all the relevant scripts
$(scripts): out
	cp src/systemd-gadget/$@ out/scripts/

# This rule copies all the relevant config files
$(configs): out
	cp src/systemd-gadget/$@ out/configs/

# This rule tells make to delete the output files
.PHONY: clean
clean:
	rm -rf out
	make -C src/uMTP-Responder/ clean
