#!/bin/bash

# Script Description:
#   This script interactively cleans up logs and output files based on user input.
#   Users can choose to remove both logs and output files, only logs, only output files, or exit without changes.

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Function to count files in a directory with a specific extension
count_files() {
    local dir="$1"
    local extension="$2"
    find "$dir" -type f -name "*.$extension" | wc -l
}

# Function to remove files in a directory with a specific extension
remove_files() {
    local dir="$1"
    local extension="$2"
    rm -f "$dir"/*.$extension
}

# Count the number of logs and output files
num_logs=$(count_files "logs" "log")
num_output_files=$(count_files "data/output" "csv")

# Check if both num_logs and num_output_files are zero
if ((num_logs == 0)) && ((num_output_files == 0)); then
    echo -e "No logs or output files found.\n"
    exit 0
fi

# Explain user options before prompting for input
echo -e "\n${GREEN}Options:${RESET}"
echo -e "  - '${YELLOW}y${RESET}' (or just press Enter): Remove both logs and output files."
echo -e "  - '${YELLOW}n${RESET}': Do not remove any files. Exit without changes."
echo -e "  - '${YELLOW}l${RESET}': Remove only logs."
echo -e "  - '${YELLOW}o${RESET}': Remove only output files."

# Display the counts and prompt the user
echo -e "\nThere are ${CYAN}$num_logs${RESET} logs and ${CYAN}$num_output_files${RESET} output files found."
read -p "Do you want to remove them? [y/n/l/o] " response

case "$response" in
    [yY]|"")
        # Remove both logs and output files
        remove_files "logs" "log"
        remove_files "data/output" "csv"
        message="Logs and output files have been removed."
        ;;
    [nN])
        # Do nothing and exit
        message="No files have been removed."
        ;;
    [lL])
        # Remove only logs
        remove_files "logs" "log"
        message="Logs have been removed."
        ;;
    [oO])
        # Remove only output files
        remove_files "data/output" "csv"
        message="Output files have been removed."
        ;;
    *)
        # Invalid input, repeat the process
        message="Invalid input. Please enter 'y', 'n', 'l', or 'o'."
        ;;
esac

# Display the result message with a newline before and after
echo -e "\n${message}${RESET}\n"