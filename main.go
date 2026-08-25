package main

import (
	"encoding/base64"
	"fmt"
	"io"
	"os"
)

func osc52(data []byte) []byte {
	encoded := base64.StdEncoding.EncodeToString(data)
	return []byte("\x1b]52;c;" + encoded + "\x07")
}

func run(r io.Reader, w io.Writer) error {
	data, err := io.ReadAll(r)
	if err != nil {
		return err
	}
	_, err = w.Write(osc52(data))
	return err
}

func main() {
	if err := run(os.Stdin, os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
