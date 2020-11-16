#!/bin/bash

_adb_complete()
{
    local cur prev
    COMPREPLY=()
    prev=("${COMP_WORDS[@]:1:COMP_CWORD-1}")
    cur="${COMP_WORDS[COMP_CWORD]}"

    # Currently, adb only takes exactly one argument
    if [ "$COMP_CWORD" = "1" ]; then
        COMPREPLY=( $(compgen -W '-h --help jenkins' -- ${cur}) )
    fi

    return 0
}
complete -F _adb_complete adb