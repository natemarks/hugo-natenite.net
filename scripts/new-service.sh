#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/new-service.sh service-name

if [ $# -eq 0 ]; then
    echo "Usage: $0 <service-name>"
    echo "Example: $0 cloud-automation"
    exit 1
fi

SERVICE_NAME="$1"

# Create the new service post using Hugo with the services archetype
hugo new "services/${SERVICE_NAME}.md" --kind services

echo "Created services/${SERVICE_NAME}.md"
echo "Edit content/services/${SERVICE_NAME}.md to customize"
