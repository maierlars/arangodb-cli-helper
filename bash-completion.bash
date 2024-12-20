#!/usr/bin/env bash

_adb_complete()
{
    local cur prev
    COMPREPLY=()
    prev=("${COMP_WORDS[@]:1:COMP_CWORD-1}")
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ "$COMP_CWORD" -lt 1 ]; then
        return
    fi

    if [ "$COMP_CWORD" -eq 1 ]; then
        COMPREPLY=( $(compgen -W '-h --help jenkins prs circleci' -- ${cur}) )
        return;
    fi

    case "${prev[0]}" in
        jenkins)
            if [ "$COMP_CWORD" -eq 2 ]; then
                COMPREPLY=( $(compgen -W 'start status watch clean' -- ${cur}) )
                return
            fi
            ;;
        circleci)
            if [ "$COMP_CWORD" -eq 2 ]; then
                COMPREPLY=( $(compgen -W 'start' -- ${cur}) )
                return
            fi
            case "${prev[-1]}" in
                -p|--param)
                    COMPREPLY=( $(compgen -W 'sanitizer replication-two nightly ui dont-cancel-pipelines' -- ${cur}) )
                    return
                    ;;
            esac
            case "${prev[-2]}" in
                -p|--param)
                    case "${prev[-1]}" in
                        sanitizer)
                            COMPREPLY=( $(compgen -W 'alubsan tsan' -- ${cur}) )
                            return
                            ;;
                        replication-two | nightly | dont-cancel-pipelines)
                            COMPREPLY=( $(compgen -W 'true false' -- ${cur}) )
                            return
                            ;;
                        ui)
                            COMPREPLY=( $(compgen -W 'off only community' -- ${cur}) )
                            return
                            ;;
                    esac
                    ;;
            esac
            COMPREPLY=( $(compgen -W '-p --param' -- ${cur}) )
            return
            ;;
        *)
            ;;
    esac

    return 0
}
complete -F _adb_complete adb
