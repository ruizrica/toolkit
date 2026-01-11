---
description: "Save work and merge to main branch with clean commit message"
---

Stage all changes, commit with a clean message, rebase from main branch. No claude or assistant in the commit message.

!git add .
!git status
!git commit -m "$ARGUMENTS"
!git checkout main
!git merge -
!git branch -d -
