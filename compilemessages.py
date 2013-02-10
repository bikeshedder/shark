#!/bin/bash

set -e

PROJECT_ROOT=$(dirname $(readlink -f $0))

# Apps have their own locale directory. Make sure to skip them
# when generating the locale for the shark project itself.
APPS="accounting billing customer"

# Make messages for all apps
ignore_glob=''
for app in $APPS; do
	ignore_glob="$ignore_glob -i $app"
	cd $PROJECT_ROOT/shark/$app
	if [ ! -d locale ] ; then
		continue
	fi
	$PROJECT_ROOT/manage.py compilemessages
done

# Make messages for project
cd $PROJECT_ROOT/shark
$PROJECT_ROOT/manage.py compilemessages
