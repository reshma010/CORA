# Consolidated Makefile for DeepStream Pose Classification
# This builds all components in the correct dependency order
# Author: Oleh Korobeyko

# Check if CUDA_VER is set, default to 12.6
CUDA_VER ?= 12.6

# Define directories relative to this Makefile location
DEEPSTREAM_DIR := ..
LIBS_DIR := $(DEEPSTREAM_DIR)/libs
APP_DIR := $(DEEPSTREAM_DIR)/app

# Component directories
SHARED_MEMORY_DIR := shared_memory
PARSERS_DIR := parsers
PREPROCESSORS_DIR := preprocessors
BODYPOSE_IMPL_DIR := bodypose_impl
MAIN_DIR := main

# Target executable name
TARGET := deepstream-pose-classification-app

# Color output for better visibility
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
.PHONY: all clean shared_memory parsers preprocessors bodypose_impl main install help

all: setup shared_memory parsers preprocessors bodypose_impl main
	@echo "$(GREEN)✓ All components built successfully!$(RESET)"
	@echo "$(CYAN)Executable: $(APP_DIR)/$(TARGET)$(RESET)"
	@echo "$(CYAN)Libraries: $(LIBS_DIR)/$(RESET)"

# Create output directories
setup:
	@echo "$(CYAN)Creating output directories...$(RESET)"
	@mkdir -p $(LIBS_DIR) $(APP_DIR)
	@export CUDA_VER=$(CUDA_VER)

# Build shared memory library first (dependency for others)
shared_memory:
	@echo "$(CYAN)Building shared memory library...$(RESET)"
	@$(MAKE) -C $(SHARED_MEMORY_DIR) clean
	@$(MAKE) -C $(SHARED_MEMORY_DIR)
	@$(MAKE) -C $(SHARED_MEMORY_DIR) install
	@if [ $$? -ne 0 ]; then \
		echo "$(RED)✗ Failed to build shared memory library$(RESET)"; \
		exit 1; \
	fi

# Build pose classification parsers
parsers:
	@echo "$(CYAN)Building pose classification parsers...$(RESET)"
	@$(MAKE) -C $(PARSERS_DIR) clean
	@$(MAKE) -C $(PARSERS_DIR)
	@if [ $$? -ne 0 ]; then \
		echo "$(RED)✗ Failed to build parsers$(RESET)"; \
		exit 1; \
	fi

# Build preprocessors
preprocessors:
	@echo "$(CYAN)Building preprocessors...$(RESET)"
	@$(MAKE) -C $(PREPROCESSORS_DIR) clean
	@$(MAKE) -C $(PREPROCESSORS_DIR)
	@if [ $$? -ne 0 ]; then \
		echo "$(RED)✗ Failed to build preprocessors$(RESET)"; \
		exit 1; \
	fi

# Build body pose implementation
bodypose_impl:
	@echo "$(CYAN)Building body pose implementation...$(RESET)"
	@$(MAKE) -C $(BODYPOSE_IMPL_DIR) clean
	@$(MAKE) -C $(BODYPOSE_IMPL_DIR)
	@if [ $$? -ne 0 ]; then \
		echo "$(RED)✗ Failed to build body pose implementation$(RESET)"; \
		exit 1; \
	fi

# Build main application (includes all subdirectories)
main: shared_memory parsers preprocessors bodypose_impl
	@echo "$(CYAN)Building main application...$(RESET)"
	@$(MAKE) -C $(MAIN_DIR) clean
	@$(MAKE) -C $(MAIN_DIR)
	@if [ $$? -ne 0 ]; then \
		echo "$(RED)✗ Failed to build main application$(RESET)"; \
		exit 1; \
	fi

# Clean all build artifacts
clean:
	@echo "$(YELLOW)Cleaning all build artifacts...$(RESET)"
	@$(MAKE) -C $(SHARED_MEMORY_DIR) clean 2>/dev/null || true
	@$(MAKE) -C $(PARSERS_DIR) clean 2>/dev/null || true
	@$(MAKE) -C $(PREPROCESSORS_DIR) clean 2>/dev/null || true
	@$(MAKE) -C $(BODYPOSE_IMPL_DIR) clean 2>/dev/null || true
	@$(MAKE) -C $(MAIN_DIR) clean 2>/dev/null || true
	@echo "$(YELLOW)Removing output directories...$(RESET)"
	@rm -rf $(LIBS_DIR)/* $(APP_DIR)/*
	@echo "$(GREEN)✓ All build artifacts cleaned$(RESET)"

# Clean only object files, keep libraries and executables
clean-obj:
	@echo "$(YELLOW)Cleaning object files only...$(RESET)"
	@find . -name "*.o" -delete
	@echo "$(GREEN)✓ Object files cleaned$(RESET)"

# Force rebuild (clean + build)
rebuild: clean all

# Install libraries and set up runtime environment
install:
	@echo "$(CYAN)Setting up library paths...$(RESET)"
	@export LD_LIBRARY_PATH=$(shell pwd)/../libs:$$LD_LIBRARY_PATH
	@echo "$(GREEN)✓ Library paths configured$(RESET)"
	@echo "$(CYAN)Add this to your ~/.bashrc for persistent setup:$(RESET)"
	@echo "export LD_LIBRARY_PATH=$(shell pwd)/../libs:\$$LD_LIBRARY_PATH"

# Run the application with default config
run:
	@if [ ! -f $(APP_DIR)/$(TARGET) ]; then \
		echo "$(RED)✗ Application not built. Run 'make all' first.$(RESET)"; \
		exit 1; \
	fi
	@echo "$(CYAN)Running DeepStream Pose Classification...$(RESET)"
	@cd $(DEEPSTREAM_DIR) && ./$(APP_DIR)/$(TARGET) --config configs/deepstream_pose_classification_config.yaml

# Show help
help:
	@echo "$(CYAN)DeepStream Pose Classification - Consolidated Build System$(RESET)"
	@echo ""
	@echo "$(GREEN)Available targets:$(RESET)"
	@echo "  $(YELLOW)all$(RESET)              - Build all components (default)"
	@echo "  $(YELLOW)clean$(RESET)            - Clean all build artifacts"
	@echo "  $(YELLOW)clean-obj$(RESET)        - Clean only object files"
	@echo "  $(YELLOW)rebuild$(RESET)          - Clean and build all"
	@echo "  $(YELLOW)install$(RESET)          - Set up library paths"
	@echo "  $(YELLOW)run$(RESET)              - Run the application with default config"
	@echo "  $(YELLOW)help$(RESET)             - Show this help message"
	@echo ""
	@echo "$(GREEN)Individual components:$(RESET)"
	@echo "  $(YELLOW)shared_memory$(RESET)    - Build shared memory library"
	@echo "  $(YELLOW)parsers$(RESET)          - Build pose classification parsers"
	@echo "  $(YELLOW)preprocessors$(RESET)    - Build preprocessors"
	@echo "  $(YELLOW)bodypose_impl$(RESET)    - Build body pose implementation"
	@echo "  $(YELLOW)main$(RESET)             - Build main application"
	@echo ""
	@echo "$(GREEN)Environment variables:$(RESET)"
	@echo "  $(YELLOW)CUDA_VER$(RESET)         - CUDA version (default: 12.6)"
	@echo ""
	@echo "$(GREEN)Examples:$(RESET)"
	@echo "  make all                    # Build everything"
	@echo "  make clean                  # Clean all artifacts"
	@echo "  make rebuild                # Clean and rebuild"
	@echo "  make run                    # Build and run application"
	@echo "  CUDA_VER=11.8 make all      # Build with specific CUDA version"