objects = $(wildcard *.in)
outputs := $(objects:.in=.txt)
compile_cmd = pip-compile

.PHONY: all clean

all: $(outputs)

%.txt: %.in
	$(compile_cmd) -v --output-file $@ $<

clean:
	rm -f $(outputs)

# Dependency chain
test.txt: base.txt
