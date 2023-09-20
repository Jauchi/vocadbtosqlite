#!/bin/bash
if ! [[ -f 'dump.zip' ]]; then
	wget 'https://vocaloid.eu/vocadb/dump.zip'
fi
mkdir -p data
unzip dump.zip -d data/
