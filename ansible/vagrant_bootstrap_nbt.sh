#!/bin/sh

/home/vagrant/src/ansible/vagrant_bootstrap.sh \
  --npm-registry http://rr-systems-live.northbristol.local:2000/ \
  --pip-index-url http://rr-systems-live.northbristol.local:2001/root/pypi/+simple/ \
  --pip-trusted-host rr-systems-live.northbristol.local
