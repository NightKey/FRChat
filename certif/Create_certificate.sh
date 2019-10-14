#!/bin/sh
openssl req -x509 -newkey rsa:4096 -keyout Key.pem -out Certification.pem -days 999 -nodes