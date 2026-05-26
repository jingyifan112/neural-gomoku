CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -pedantic
LDFLAGS ?= -lm

all: test_infer play_c

test_infer: test_infer.o cnn_infer.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

play_c: play_c.o cnn_infer.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c cnn_infer.h
	$(CC) $(CFLAGS) -c -o $@ $<

test: test_infer
	./test_infer weights/9x9_weights.bin reference/case0

clean:
	rm -f *.o test_infer play_c

.PHONY: all clean test
