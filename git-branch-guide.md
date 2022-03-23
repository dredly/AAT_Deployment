# Git Branch Guide
made by Richard Jackson (7th March 2022)
version 0.1

- All instructions are made through a local CLI, no GitLab UI.

// Make sure repo is cloned correctly

## Make sure main is up-to-date
[main] $ git pull

## Create branch
[main] $ git branch [localBranch]

## Move to new branch
[main] $ git checkout [localBranch]

[...DO CODING GOOD...]

## Add & commit new changes on [localBranch]
[localBranch] $ git commit -am "useful commit message"

[ Optional: Push branch to Lab (need GlobalProtech ]
[localBranch] $ git push --set-upstream origin [localBranch]

## Move to main branch
[localBranch] $ git checkout main

## Make sure main is up-to-date (again!)
[main] $ git pull

## Merge local changes to main
[main] $ git merge [localBranch]

## Push main to remoteMon
[main] $ git push

## Deleting branches
Source: https://www.freecodecamp.org/news/how-to-delete-a-git-branch-both-locally-and-remotely/

// delete branch locally
[main] $ git branch -d [localBranchName]

// delete branch remotely
[main] $ git push origin --delete [remoteBranchName]
