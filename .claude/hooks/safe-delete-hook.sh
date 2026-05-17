#!/bin/bash
# Hook to set up safe delete: alias rm to trash and provide rm! for permanent delete
alias rm='trash'
rm!() {
    command rm "$@"
}