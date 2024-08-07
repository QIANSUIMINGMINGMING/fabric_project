#!/bin/bash

# Usage function to display help
usage() {
    echo "Usage: $0 -f <yaml_file> -c <command>"
    echo "  -f <yaml_file>  Path to the YAML file with hosts."
    echo "  -c <command>    Command to run with fab."
    exit 1
}

# Parse command-line arguments
while getopts "f:c:" opt; do
    case ${opt} in
        f )
            YAML_FILE=$OPTARG
            ;;
        c )
            COMMAND=$OPTARG
            ;;
        \? )
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Check if the required arguments are provided
if [ -z "${YAML_FILE}" ] || [ -z "${COMMAND}" ]; then
    usage
fi

# Check if yq is installed
if ! command -v yq &> /dev/null; then
    echo "yq could not be found, please install it to use this script."
    exit 1
fi

# Read the hosts from the YAML file
HOSTS=$(yq eval '.hosts | join(",")' "$YAML_FILE")

# Construct and run the fab command
fab -H "$HOSTS" "$COMMAND"