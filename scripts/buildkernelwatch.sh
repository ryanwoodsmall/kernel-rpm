#!/bin/bash

watch -n1 "uptime ; echo ; vmstat ; echo ; ccache -s ; echo ; stat --format='%x|%y' /tmp/kernelbuild.out | tr '|' '\n' ; echo ; tail -3 /tmp/kernelbuild.out"
