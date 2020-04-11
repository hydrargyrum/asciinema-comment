#!/bin/sh -e
# usage: $0 ASCIINEMA_ARGS
#
# This program wraps "asciinema rec", by running it in GNU screen
# configured to have a blank line reserved at the bottom of the display, like
# a status bar.
# Commands recorded by asciinema will not be able to display anything on this
# bar.
#
# This is useful for editing the asciinema record afterwards, for example to
# put "subtitles" on the bar, without hiding any useful lines of the display.

# license: public domain, see LICENSE file

line=last
if [ "$1" = "--top" ]
then
    line=first
fi

screencfg=$(mktemp -t rec.screen.XXXXXX)
trap "rm '$screencfg'" EXIT

cat > "$screencfg" << EOF
hardstatus always${line}line
hardstatus string " "
altscreen on
EOF

asciinema rec -c "screen -c $screencfg" "$@"
