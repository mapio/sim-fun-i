grab_and_clean() {
  "$@" 2>&1 | sed $'s,\x1b\\[[0-9;]*[a-zA-Z],,g'
}
