import json
import sys
import re
from . import requests_with_caching

"""
complete_discography.py

Assemble a complete discography for an artist based on "Aliases" and "In Groups" data from Discogs.com.

Input: Artist name

Output: HTML table of all albums by all artists for which the given artist is an alias or a group member.

Usage: python complete_discography.py [artist name] > outfile.html

Written by Daniel Lovette
https://github.com/dfunklove
"""

PARSER = 'lxml'
BASE_URL = 'https://api.discogs.com'
API_KEY = 'EtNnhmPqmhSULCVJHRRx'
API_SECRET = 'VLSajjYuNLcuDKeRQzmrwwhnKlRYBLsn'

def find_artist_id(name):
	"Query the discogs api to get an artist id for the given name"

	if not name:
		return None

	url = BASE_URL + "/database/search"
	params = { 'anv': name, 'key': API_KEY, 'secret': API_SECRET }
	response = requests_with_caching.get(url, params)
	result = json.loads(response.text)
	#print(response.url)
	#print(json.dumps(result, indent=2))

	first = result['results'][0]
	if first['type'] == 'artist':
		return first['id']
	else:
		return None


def find_artist_info(artist_id):
	"Query the discogs api to get info for the given artist id"

	if not artist_id:
		return None

	url = f"{BASE_URL}/artists/{artist_id}"
	response = requests_with_caching.get(url)
	return json.loads(response.text)


def find_releases(artist_id):
	"Query the discogs api to get all releases for the given artist id"

	if not artist_id:
		return None

	url = f"{BASE_URL}/artists/{artist_id}/releases"
	response = requests_with_caching.get(url)
	result = json.loads(response.text)

	# put results in a dict to guarantee uniqueness
	retval = {}
	for i in result['releases']:
		if i['role']=='Main':
			retval[i['id']] = i
	return retval


def disco_table(releases):
	"Accept release data from discogs api and put it in an html table"

	# artist title label catno country year

	fields = ['artist', 'title', 'label', 'year']
	output = "<table><tr>"
	for f in fields:
		pretty = f.capitalize()
		output += f"<th>{pretty}</th>"
	output += "</tr>\n"
	for r in releases:
		output += "<tr>"
		for f in fields:
			if f in r:
				output += f"<td>{r[f]}</td>"
			else:
				output += "<td></td>"
		output += "</tr>\n"
	output += "</table>"

	return output


def get_discography(name):
	"""
	Assemble a complete discography for an artist based on "Aliases" and "In Groups" data from Discogs.com

	Input: artist name
	Output: html table of releases by artist
	"""

	artist_id = find_artist_id(name)
	#print(f"artist_id = {artist_id}")

	artist_info = find_artist_info(artist_id)
	#print(json.dumps(artist_info, indent=2))

	all_releases = find_releases(artist_id)

	for alias in artist_info['aliases']:
		all_releases.update(find_releases(alias['id']))

	for group in artist_info['groups']:
		all_releases.update(find_releases(group['id']))

	#print(json.dumps(all_releases, indent=2))
	#print(len(all_releases))

	return disco_table(all_releases.values())

#
# Main Program
#
if __name__ == '__main__':
	if (len(sys.argv) < 2):
		print("Usage: python "+sys.argv[0]+" [artist name] > outfile.html")
		exit()

	get_discography(sys.argv[1])