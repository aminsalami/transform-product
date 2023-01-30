#!/usr/bin/env bash

pip3 install --target ./package -r requirements.txt
cd package
zip -r ../deployment-package.zip .
cd ..
zip -r deployment-package.zip etl/
