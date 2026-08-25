package main

import (
	"bytes"
	"testing"
)

func TestRun(t *testing.T) {
	var out bytes.Buffer
	err := run(bytes.NewBufferString("hello"), &out)
	if err != nil {
		t.Fatal(err)
	}
	got := out.String()
	want := "\x1b]52;c;aGVsbG8=\x07"
	if got != want {
		t.Fatalf("got %q want %q", got, want)
	}
}

func BenchmarkRun1KiB(b *testing.B) {
	input := bytes.Repeat([]byte("a"), 1024)
	for b.Loop() {
		var out bytes.Buffer
		if err := run(bytes.NewReader(input), &out); err != nil {
			b.Fatal(err)
		}
	}
}
