SHELL=/bin/bash

build:
	stacker build -r us-west-2 conf/lunohq/development.env conf/lunohq/config.yaml $(params)

outputs:
	stacker info -r us-west-2 conf/lunohq/development.env conf/lunohq/config.yaml $(params)

build-prod:
	stacker build -r us-east-1 conf/lunohq/production.env conf/lunohq/config.yaml $(params)

outputs-prod:
	stacker info -r us-east-1 conf/lunohq/production.env conf/lunohq/config.yaml $(params)

update-blueprints:
	pip install -e .

seal:
	tar cvf ssl.tar.gz ssl
	keybase encrypt mhahn ssl.tar.gz
	rm -rf ssl
	rm ssl.tar.gz

unseal:
	keybase decrypt ssl.tar.gz.asc -o ssl.tar.gz
	tar xzvf ssl.tar.gz

encrypt:
	aws --region us-east-1 kms encrypt --key-id alias/stacker --plaintext $(value) --output text --query CiphertextBlob
