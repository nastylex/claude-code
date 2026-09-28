#!/usr/bin/env bash
# Find a working Python 3 interpreter and exec the hook with it.
#
# Mirrors security-guidance's sg-python.sh: on Windows + Git Bash, `python3`
# can resolve to the Microsoft Store stub that exits 49 silently. Probe each
# candidate and skip any that fails or is Python 2.
#
# Args after the shim path are passed straight through to the interpreter.
set -e

probe() {
    # $1..N: the interpreter command (may be multi-word like `py -3`)
    # Probe writes the major version to stdout and exits 0 iff it's >=3.
    "$@" -c 'import sys; print(sys.version_info[0])' 2>/dev/null
}

for cmd in "python3" "python" "py -3"; do
    # Word-split intentionally so `py -3` works
    # shellcheck disable=SC2086
    v=$(probe $cmd) || continue
    if [ "$v" = "3" ]; then
        # shellcheck disable=SC2086
        exec $cmd "$@"
    fi
done

echo "speech: no working Python 3 interpreter found." >&2
echo "  tried: python3, python, py -3" >&2
echo "  on Windows, install Python from https://python.org (NOT the Microsoft Store)" >&2
exit 0
