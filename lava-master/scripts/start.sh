#!/bin/bash

#/setup.sh || exit $?

cp /setup.sh /root/entrypoint.d/
# TODO remove this when the PR is used in any release
sed -i 's,^for f in /root/entrypoint.d/.*,for f in $(find /root/entrypoint.d/ -type f); do,' /root/entrypoint.sh

/root/entrypoint.sh
exit 0

