#!/usr/bin/env bash
set -euo pipefail

BUCKET="natenite-production-site-content"
PUBLIC_DIR="public"

echo "Building site..."
hugo --minify --cleanDestinationDir

echo "Deploying to s3://${BUCKET}..."
aws s3 sync "${PUBLIC_DIR}/" "s3://${BUCKET}/" \
    --delete \
    --cache-control "public, max-age=3600"

echo "Deployment complete!"
echo "Site: https://natenite.net"
