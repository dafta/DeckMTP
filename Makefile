# This is the default target, which will be built when
# you invoke make
.PHONY: all
all: deploy

# This rule creates the output directories
.PHONY: build
build:
	cli/decky plugin build

# This rule tells make to delete the output files
.PHONY: deploy
deploy:
	cli/decky plugin deploy
