#!/bin/bash -x
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Aug 03, 2022  8794      sharbison    Initial copy of build container
#                                         scripts from dev_rhel8, to be
#                                         converted to rhel7.
#

# Moves all required resources over to the build's baseline dir.
# Does not modify the git repos.

repo="$1"
shift

pushd .
if [ -d "$repo" ]
then
   cd $repo
else
   echo "Unable to find repo: $repo"
   popd
   exit 1
fi

git_branch="$1"
shift
baseline="$1"
shift
parts_to_synch="$*"

echo "Git Repository $repo"
cd $repo

# Show the current HEAD for this repo.
git log --pretty=format:'%ci [%h] <%an> %s' --date-order  -1

if [ ! -d "$baseline" ]; then
   mkdir -p $baseline
fi

echo "Synching:  $parts_to_synch"
rsync -ruql $parts_to_synch $baseline
if [ $? -ne 0 ]; then
   exit 1
fi
popd

exit

