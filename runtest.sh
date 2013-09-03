#!/bin/sh
mkdir -p ~/rpmbuild/RHEL6/noarch
mkdir -p ~/rpmbuild/RHEL6/x86_64
mkdir -p ~/rpmbuild/RHEL6/other_rpms
mkdir -p ~/rpmbuild/www/RHEL6-x86_64/test
./buildrpmrepo.py --base ~/rpmbuild --version RHEL6 --arch x86_64 --repo test --report --unsigned --fake $*
