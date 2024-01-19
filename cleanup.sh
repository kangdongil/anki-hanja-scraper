#!/bin/bash

# Count the number of logs and output files
num_logs=$(find logs -type f -name "*.log" | wc -l)
num_output_files=$(find data/output -type f -name "*.csv" | wc -l)

# Check if both num_logs and num_output_files are zero
if [ "$num_logs" -eq 0 ] && [ "$num_output_files" -eq 0 ]; then
    echo "No logs or output files found. Exiting without changes."
    exit 0
fi

# Explain user options before prompting for input
echo -e "\nPlease choose an option:"
echo "  - 'y' (or just press Enter): Remove both logs and output files."
echo "  - 'n': Do not remove any files. Exit without changes."
echo "  - 'l': Remove only logs."
echo "  - 'o': Remove only output files."

# Display the counts and prompt the user
echo -e "\nThere are $num_logs logs and $num_output_files output files found."

read -p "Do you want to remove them? [y/n/l/o] " response

case "$response" in
    [yY]|"")
        # Remove both logs and output files
        rm -f logs/*.log
        rm -f data/output/*.csv
        echo "Logs and output files have been removed."
        ;;
    [nN])
        # Do nothing and exit
        echo "No files have been removed."
        ;;
    [lL])
        # Remove only logs
        rm -f logs/*.log
        echo "Logs have been removed."
        ;;
    [oO])
        # Remove only output files
        rm -f data/output/*.csv
        echo "Output files have been removed."
        ;;
    *)
        # Invalid input, repeat the process
        echo "Invalid input. Please enter 'y', 'n', 'l', or 'o'."
        ;;
esac