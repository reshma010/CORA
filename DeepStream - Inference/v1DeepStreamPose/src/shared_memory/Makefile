CC = gcc
CXX = g++
CFLAGS = -std=c99 -fPIC -Wall -Wextra -O2
CXXFLAGS = -std=c++14 -fPIC -Wall -Wextra -O2
LDFLAGS = -shared -pthread -lrt

TARGET = libshared_memory.so
SOURCES = shared_memory.c
HEADERS = shared_memory.h
OBJECTS = $(SOURCES:.c=.o)

# Default target
all: $(TARGET)

# Build shared library
$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^

# Build object files
%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f $(OBJECTS) $(TARGET)

# Install library (optional)
install: $(TARGET)
	cp $(TARGET) ../../libs/
	cp $(HEADERS) ../../libs/

.PHONY: all clean install