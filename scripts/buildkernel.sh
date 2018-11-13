#!/bin/bash

if [ -e /tmp/kernelbuild.out ] ; then
	tail -5 /tmp/kernelbuild.out
	rm -f /tmp/kernelbuild.out
fi
date
( time ( rpmbuild -ba --clean ${HOME}/rpmbuild/SPECS/kernel.spec ) ) >/tmp/kernelbuild.out 2>&1 
date
