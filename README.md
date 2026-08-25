# osc52

Copy stuff using [OSC 52](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h3-Operating-System-Commands).

It reads standard input, base64-encodes it, and writes `ESC ] 52 ; c ; <base64> BEL`
to your terminal — so whatever you pipe into it lands on the system clipboard, even
over SSH. Think `pbcopy`, but it works wherever your terminal is.

```sh
echo "hello" | osc52
cat notes.txt | osc52
git log -1 --format=%H | osc52
```

## Install

With [mise](https://mise.jdx.dev/):

```sh
mise use -g github:dtinth/osc52
```

Or grab a binary from [releases](https://github.com/dtinth/osc52/releases) —
static builds for Linux (x86_64, aarch64) and macOS (Intel, Apple silicon).

## Notes

- Your terminal has to support OSC 52 and allow writing to the clipboard.
  Most do: kitty, WezTerm, Ghostty, foot, Alacritty, Windows Terminal. In
  iTerm2 it is *Settings → General → Selection → Applications in terminal may
  access clipboard*.
- Inside tmux, turn on `set -g set-clipboard on` and tmux will forward the
  sequence to the outer terminal for you.
- Terminals cap how much they will accept — xterm's default is under 100 KB —
  so this is for text, not for piping a disk image.
- The escape sequence is written to `/dev/tty`, not to stdout, so it never
  leaks into a pipe or a redirect — and it still reaches your terminal when
  stdout is redirected. With no terminal at all (in a cron job, say) it falls
  back to stderr.

## Build

```sh
make        # builds ./osc52
make check  # builds, then runs the tests (Python 3, stdlib only)
```

Roughly 60 lines of C, no dependencies. On Linux the Makefile picks up
`musl-gcc` when it is installed, which is how the released binaries — about
5 KB, fully static — are built. It encodes at just under 1 GB/s and a run
with a small payload costs about 0.3 ms, most of which is `execve`.

## Releasing

Releases cut themselves. A push to `main` carrying a `feat:`, `fix:`, `perf:`
or a breaking change ([Conventional
Commits](https://www.conventionalcommits.org/)) builds all four targets, tags
the next version and publishes it; `docs:`, `chore:` and friends release
nothing. Before 1.0 a breaking change bumps the minor rather than the major.
To force a particular version, run the Release workflow by hand and give it
one — left empty it builds without publishing.

## License

MIT
