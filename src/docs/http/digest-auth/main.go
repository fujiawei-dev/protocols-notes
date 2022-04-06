/*
 * @Date: 2022.04.06 10:24
 * @Description: Omit
 * @LastEditors: Rustle Karl
 * @LastEditTime: 2022.04.06 19:45:07
 */

package main

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"net/textproto"
	"strings"
	"unsafe"
)

func main() {
	// fmt.Printf("%x\n", md5.Sum([]byte("OK")))

	authValue := `Digest username="Mufasa",
		realm="testrealm@host.com",
		nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
		uri="/dir/index.html",
		qop=auth,
		nc=00000001,
		cnonce="0a4f113b",
		response="6629fae49393a05397450978507c4ef1",
		opaque="5ccc069c403ebaf9f0171e9517f40e41"`

	d := readDigest(authValue)
	d.Validate("Circle Of Life", "GET", nil)
}

type Digest struct {
	Username  string `json:"username,omitempty"`
	Realm     string `json:"realm,omitempty"`
	Nonce     string `json:"nonce,omitempty"`
	Uri       string `json:"uri,omitempty"`
	Algorithm string `json:"algorithm,omitempty"`
	Cnonce    string `json:"cnonce,omitempty"`
	Nc        string `json:"nc,omitempty"`
	Qop       string `json:"qop,omitempty"`
	Response  string `json:"response,omitempty"`
}

func (d *Digest) Validate(password, method string, body []byte) bool {
	if d == nil {
		return false
	}

	var (
		ha0      [md5.Size]byte
		ha1      [md5.Size]byte
		ha2      [md5.Size]byte
		response [md5.Size]byte
	)

	if d.Algorithm == "MD5-sess" {
		ha0 = md5.Sum(StringToBytes(d.Username + ":" + d.Realm + ":" + password))
		ha1 = md5.Sum(StringToBytes(hex.EncodeToString(ha0[:]) + ":" + d.Nonce + ":" + d.Cnonce))
	} else { // MD5
		ha1 = md5.Sum(StringToBytes(d.Username + ":" + d.Realm + ":" + password))
	}

	// fmt.Printf("HA1 = %x\n", ha1)

	if d.Qop == "auth-int" {
		ha0 = md5.Sum(body)
		ha2 = md5.Sum(StringToBytes(method + ":" + d.Uri + ":" + BytesToString(ha0[:])))
	} else {
		ha2 = md5.Sum(StringToBytes(method + ":" + d.Uri))
	}

	// fmt.Printf("HA2 = %x\n", ha2)

	var responseStr string

	if d.Qop == "auth" || d.Qop == "auth-int" {
		responseStr = hex.EncodeToString(ha1[:]) + ":" + d.Nonce + ":" + d.Nc +
			":" + d.Cnonce + ":" + d.Qop + ":" + hex.EncodeToString(ha2[:])
	} else {
		responseStr = hex.EncodeToString(ha1[:]) + ":" + d.Nonce + ":" + hex.EncodeToString(ha2[:])
	}

	// fmt.Printf("responseStr = %s\n", responseStr)
	response = md5.Sum(StringToBytes(responseStr))
	// fmt.Printf("L = %s\n", d.Response)
	// fmt.Printf("R = %x\n", response)

	return hex.EncodeToString(response[:]) == d.Response
}

// StringToBytes converts string to byte slice without a memory allocation.
func StringToBytes(s string) []byte {
	return *(*[]byte)(unsafe.Pointer(
		&struct {
			string
			Cap int
		}{s, len(s)},
	))
}

// BytesToString converts byte slice to string without a memory allocation.
func BytesToString[T []byte | [md5.Size]byte](b T) string {
	return *(*string)(unsafe.Pointer(&b))
}

func assertBool(guard bool, text string) {
	if !guard {
		panic(text)
	}
}

func readDigest(authValue string) *Digest {
	if len(authValue) == 0 {
		return nil
	}

	sp := strings.Index(authValue, " ")
	if sp < strings.Index(authValue, ",") {
		authValue = authValue[sp+1:]
	}

	pairs := make(map[string]string, strings.Count(authValue, ";"))
	authValue = textproto.TrimString(authValue)

	var part string
	for len(authValue) > 0 { // continue since we have rest
		part, authValue, _ = strings.Cut(authValue, ",")
		if part = textproto.TrimString(part); part != "" {
			key, value, _ := strings.Cut(part, "=")
			if val, ok := parseDigestValue(value, true); ok {
				pairs[strings.ToLower(key)] = val
			}
		}
	}

	return &Digest{
		Username:  pairs["username"],
		Realm:     pairs["realm"],
		Nonce:     pairs["nonce"],
		Uri:       pairs["uri"],
		Algorithm: pairs["algorithm"],
		Cnonce:    pairs["cnonce"],
		Nc:        pairs["nc"],
		Qop:       pairs["qop"],
		Response:  pairs["response"],
	}
}

func validDigestValueByte(b byte) bool {
	return 0x20 <= b && b < 0x7f && b != '"' && b != ';' && b != '\\'
}

func parseDigestValue(raw string, allowDoubleQuote bool) (string, bool) {
	// Strip the quotes, if present.
	if allowDoubleQuote && len(raw) > 1 && raw[0] == '"' && raw[len(raw)-1] == '"' {
		raw = raw[1 : len(raw)-1]
	}
	for i := 0; i < len(raw); i++ {
		if !validDigestValueByte(raw[i]) {
			return "", false
		}
	}
	return raw, true
}
