#!/usr/bin/env bash
set -e
mkdir -p secrets
if [ ! -f secrets/jwt_secret.txt ]; then
  openssl rand -hex 32 > secrets/jwt_secret.txt
  chmod 600 secrets/jwt_secret.txt
  echo "JWT secret created at secrets/jwt_secret.txt"
else
  echo "JWT secret already exists."
fi
