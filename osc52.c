/*
 * osc52 - copy standard input to the system clipboard using OSC 52.
 *
 * Reads stdin, base64-encodes it as it goes, and writes the escape sequence
 * ESC ] 52 ; c ; <base64> BEL to the controlling terminal (/dev/tty), falling
 * back to stderr when there is no terminal to write to.
 */

#include <fcntl.h>
#include <unistd.h>

static const char B64[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

#define CHUNK 49152 /* bytes read at a time; a multiple of 3 */

static int tty;
static unsigned char in[CHUNK];
static char out[CHUNK / 3 * 4];

static void emit(const char *buf, int len) {
	while (len > 0) {
		int n = (int)write(tty, buf, (size_t)len);
		if (n <= 0) _exit(1);
		buf += n;
		len -= n;
	}
}

/* Encode n bytes of `in` into `out`, padding with '=' if n is not a
   multiple of 3, and return how many bytes of `out` were filled. */
static int encode(int n) {
	int i, o = 0;
	for (i = 0; i < n; i += 3) {
		int left = n - i;
		unsigned long v = (unsigned long)in[i] << 16;
		if (left > 1) v |= (unsigned long)in[i + 1] << 8;
		if (left > 2) v |= in[i + 2];
		out[o++] = B64[v >> 18 & 63];
		out[o++] = B64[v >> 12 & 63];
		out[o++] = left > 1 ? B64[v >> 6 & 63] : '=';
		out[o++] = left > 2 ? B64[v & 63] : '=';
	}
	return o;
}

int main(void) {
	int kept = 0, n, full, i;

	tty = open("/dev/tty", O_WRONLY);
	if (tty < 0) tty = 2;

	emit("\033]52;c;", 7);
	/* Encode whole 3-byte groups per read; carry the odd 1-2 bytes over. */
	while ((n = (int)read(0, in + kept, (size_t)(CHUNK - kept))) > 0) {
		n += kept;
		full = n - n % 3;
		emit(out, encode(full));
		kept = n - full;
		for (i = 0; i < kept; i++) in[i] = in[full + i];
	}
	if (kept) emit(out, encode(kept));
	emit("\007", 1);
	return n < 0; /* nonzero if stdin could not be read to the end */
}
