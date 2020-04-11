# Edit an `asciinema` cast to insert subtitles

`asciinema` is a tool to record shell sessions and then replay them.
This is useful for demonstrating features or showing how to use an app.

However, it may be useful to show "subtitles" during the cast, about what is currently being shown.
Some people solve this problem by typing shell comments during the record, but this is tedious.
And it works only for a shell, not for showing an ncurses app.

This repository contain helpers for post-processing the cast file and inserting subtitles after recording, but before publishing the cast.

# Recording

Replace the usual:

	asciinema rec my-record.cast

With:

	record-with-bar.sh my-record.cast

`record-with-bar` wraps "asciinema rec", by running it in GNU screen configured to have a blank line reserved at the bottom of the display, like a status bar.
This reserved bar will be exploitable during cast editing to display the subtitles without hiding any useful lines of the display.

`record-with-bar` is a simple wrapper to `asciinema rec`, so you can use all usual arguments supported by `asciinema rec`, for example `--idle-time-limit`.

Now, record the asciinema cast as usual.

# Editing the cast

## Finding timestamps

Then, comes the editing phase.
First, you have to identify at which timestamps you want to insert subtitles.

This can be done with:

	asciinema play --show-timer my-record.cast

And pressing "space" to pause playback, and then "." to advance frame by frame if needed.
With `--show-timer`, the timestamp of each frame is displayed.

## Subtitles file

Then, write a subtitles file. A subtitles file consists in multiple line, each line giving an instruction for one message.
A line typically has this syntax:

	<timestamp> <message>

This instructs to show a message at a given timestamp. The message will stay until it is replaced by another message or until it is cleared.
For example:

	1 This message will show at timestamp 1 second.

It is possible to clear the message with just:

	<timestamp>

For example:

	3

With the script:

	1 This message will show at timestamp 1 second.
	3

The message shown at t=1s will be erased at t=3s.

There's a shorthand to give a time span for a message:

	1-3 This message will show at t=1 second and disappear at t=3.

Instead of giving an end timestamp, a duration can be used:

	1:2 This message will show at t=1 second and will last for 2 seconds.

Decimal numbers can be used for timestamps, for example `1.5`.

## Combining cast and subtitles

When the subtitles file has been written, it is possible to produced a new cast file combining the original cast with the subtitles:

	insert-comments.py my-record.cast my-subtitles.txt record-with-subtitles.cast

`record-with-subtitles.cast` is the resulting cast with subtitles, which can be played or published as any regular asciinema file.
`my-record.cast` is left untouched.

