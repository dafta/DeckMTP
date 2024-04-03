# All the systemd files that need to be copied to output
systemd := umtprd.service
systemd += gadget
systemd += gadget-init.service gadget-init.sh
systemd += gadget-start.service gadget-start.sh
systemd += usbgadget-func-mtp.service

# This is the default target, which will be built when
# you invoke make
.PHONY: all
all: umtprd $(systemd)

# This rule creates the output directory
out:
	mkdir -p out

# This rule tells make how to build the MTP responder
umtprd: out
	# Enable USB 3.0 support
	sed -i -e 's%//#define CONFIG_USB_SS_SUPPORT 1%#define CONFIG_USB_SS_SUPPORT 1%' src/uMTP-Responder/inc/buildconf.h

	# Build uMTP-Reponder
	make -C src/uMTP-Responder/

	# Copy output to output directory there
	cp src/start.sh out/
	cp src/stop.sh out/
	cp src/umtprd.conf out/
	cp src/uMTP-Responder/umtprd out/

# This rule copies all the relevant systemd files
$(systemd): out
	cp src/systemd-gadget/$@ out/

# This rule tells make to delete the output files
.PHONY: clean
clean:
	rm -rf out
	make -C src/uMTP-Responder/ clean
