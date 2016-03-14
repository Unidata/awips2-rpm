#!/bin/bash -x

#
# Moves all required resources over to the builds baseline dir.
# This script will also reset and clean the git repos! 
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial import from awipscm

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

echo "Reset workspace to HEAD"
git reset --hard HEAD

echo "Clean workspace"
git clean -df

echo "Checkout $repo:${git_branch}"
git checkout ${git_branch}
if [ $? -ne 0 ]; then
   popd
   exit 1
fi

git pull
if [ $? -ne 0 ]; then
   popd
   exit 1
fi

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

exit 0
