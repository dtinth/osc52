CFLAGS ?= -Os -std=c99 -Wall -Wextra -pedantic
CFLAGS += -fno-asynchronous-unwind-tables -fno-unwind-tables \
          -ffunction-sections -fdata-sections

ifeq ($(shell uname -s),Darwin)
CFLAGS += -mmacosx-version-min=11.0
LDFLAGS += -Wl,-dead_strip
STRIPFLAGS = -x
else
# musl links a fully static binary a fraction of the size of a glibc one
ifeq ($(origin CC),default)
CC := $(shell command -v musl-gcc || echo cc)
endif
LDFLAGS += -static -Wl,--gc-sections -Wl,--build-id=none -Wl,-z,noseparate-code
STRIPFLAGS = -s
endif

osc52: osc52.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<
	strip $(STRIPFLAGS) $@

check: osc52
	python3 tests/test_osc52.py ./osc52

clean:
	rm -f osc52

.PHONY: check clean
