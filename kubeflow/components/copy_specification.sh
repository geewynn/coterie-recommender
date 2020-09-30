#!/bin/sh

BUCKET="your-bucket-name"

echo "\nCopy component specifications to Google Cloud Storage"
gsutil cp preprocess/component.yaml gs://${BUCKET}/components/preprocess/component.yaml
gsutil acl ch -u AllUsers:R gs://${BUCKET}/components/preprocess/component.yaml

