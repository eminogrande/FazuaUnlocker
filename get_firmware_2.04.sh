#!/bin/sh
# Fetch the original FAZUA evation firmware 2.04 from the Internet Archive
# (snapshot of fazua.com/documents/826, 2022-07-09) and verify its SHA-256.
set -e
F=evation_Software_2.04.bin
URL="https://web.archive.org/web/20220709185915id_/https://fazua.com/documents/826/$F"
SHA=8fe885c9dfc7caa9cf8e61b88051bf8d42da53747c4fd86d2b72c3c2ef23d32e
curl -fL -o "$F" "$URL"
echo "$SHA  $F" | shasum -a 256 -c
