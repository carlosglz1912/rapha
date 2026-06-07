#compdef rapha rapha-backup rapha-calendar rapha-contacts rapha-cookbook rapha-docs rapha-gallery rapha-mail rapha-mcp rapha-memory rapha-notes rapha-personal rapha-preset rapha-research rapha-sessions rapha-signature rapha-skills rapha-tasks rapha-theme rapha-webhook
# Zsh tab-completion for the rapha umbrella + sub-CLIs.
#
# Drop in any directory on $fpath, e.g.:
#     fpath=(/path/to/rapha-ui/scripts/_completion $fpath)
#     autoload -U compinit; compinit
#
# Then `rapha <tab>` completes subcommands; `rapha mail <tab>`
# completes mail subcommands; `rapha-mail <tab>` works the same.

_rapha_scripts_dir() {
    local self="${(%):-%x}"
    while [[ -L "$self" ]]; do self="$(readlink "$self")"; done
    cd "${self:h}/.." && pwd
}

typeset -gA _rapha_subs

_rapha_refresh() {
    _rapha_subs=()
    local dir="$(_rapha_scripts_dir)"
    local py="$dir/../venv/bin/python"
    [[ -x "$py" ]] || py="$(command -v python3)"
    local f sub help_out commands
    for f in "$dir"/rapha-*; do
        [[ -x "$f" ]] || continue
        case "$f" in
            *.bak|*.pyc|*.pre-*) continue ;;
        esac
        sub="${${f:t}#rapha-}"
        help_out=$("$py" "$f" --help 2>/dev/null) || continue
        commands=$(echo "$help_out" | grep -oE '\{[a-z0-9_,-]+\}' | head -1 \
            | tr -d '{}' | tr ',' ' ')
        _rapha_subs[$sub]="$commands"
    done
}

_rapha() {
    [[ ${#_rapha_subs} -eq 0 ]] && _rapha_refresh

    local cmd="${words[1]}"

    if [[ "$cmd" == "rapha" ]]; then
        if (( CURRENT == 2 )); then
            local -a subs=(${(k)_rapha_subs} help)
            _describe 'subcommand' subs
            return
        fi
        local sub="${words[2]}"
        if [[ "$sub" == "help" ]] && (( CURRENT == 3 )); then
            local -a subs=(${(k)_rapha_subs})
            _describe 'subcommand' subs
            return
        fi
        if (( CURRENT == 3 )); then
            local -a sc=(${(s/ /)_rapha_subs[$sub]})
            _describe 'command' sc
            return
        fi
        return
    fi

    # rapha-foo <tab>
    local sub="${cmd#rapha-}"
    if (( CURRENT == 2 )); then
        local -a sc=(${(s/ /)_rapha_subs[$sub]})
        _describe 'command' sc
        return
    fi
}

_rapha "$@"
