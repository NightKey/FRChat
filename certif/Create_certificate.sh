#!/bin/sh
openssl req -x509 -newkey rsa:4096 -keyout PublicKey.pem -out PrivateKey.pem -days 999 -nodes