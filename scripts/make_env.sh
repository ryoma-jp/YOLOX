#! /bin/bash

cat <<EOF > .env
UID=$(id -u)
GID=$(id -g)
UNAME=yolox
EOF
