#!/bin/python
# This scripts makes use of the http://markup.su/highlighter/ API to do syntax highlighting for code to be published in blogger.

import requests
import sys

def print_usage():
	print "Usage: blogger-code.py <langugae> <source code file>"

def main():
	if len(sys.argv) is not 3:
		print_usage()
		sys.exit(0)

	language = sys.argv[1]

	with open(sys.argv[2], 'r') as code_file:
		code = code_file.read()

	payload = {"language": language, "theme": "Active4D", "source": code}
	r = requests.get('http://markup.su/api/highlighter', params=payload)
	print r.content

if __name__ == '__main__':
	main()
