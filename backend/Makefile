# This is the default target, which will be built when
# you invoke make
.PHONY: all
all: umtprd out

# This rule tells make how to build the MTP responder
umtprd:
	# Clone the MTP submodule
	git submodule update --init --recursive
	# This enables USB 3.0 support
	sed -i -e 's%//#define CONFIG_USB_SS_SUPPORT 1%#define CONFIG_USB_SS_SUPPORT 1%' ./src/uMTP-Responder/inc/buildconf.h
	make -C src/uMTP-Responder/

# This rule creates the output directories and copies the files there
out:
	mkdir -p ./out
	cp ./src/start.sh ./out/
	cp ./src/stop.sh ./out/
	cp ./src/umtprd.conf ./out/
	cp ./src/uMTP-Responder/umtprd ./out/

# This rule tells make to delete the output files
.PHONY: clean
clean:
	rm -rf ./out
	make -C src/uMTP-Responder/ clean
