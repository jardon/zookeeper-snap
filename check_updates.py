#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import requests
import subprocess
import re
import yaml
from bs4 import BeautifulSoup
from pathlib import Path

def _get_releases():
    URL = "https://dlcdn.apache.org/zookeeper/"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    releases = []

    links = soup.find_all('a')
    for link in links:
        short_link = link['href'][:-1]
        if 'zookeeper-' in short_link:
            releases.append(short_link[10:])
    return releases

def _get_branch_versions():
    git_branch = subprocess.run(["git", "branch", "-r", "-q"], capture_output=True, text=True).stdout
    short_versions = list(set(re.findall("\d.\d+", git_branch)))
    versions = []
    for version in short_versions:
        subprocess.run(["git", "checkout", f"{version}/stable", "-q"])
        long_version = yaml.safe_load(Path('snap/snapcraft.yaml').read_text())['version']
        versions.append(long_version)
    return versions


def diff_versions():
    branches = _get_branch_versions()
    return [ x for x in _get_releases() if x not in branches ]

def diff_versions_short():
    return [ get_short_version(x) for x in diff_versions() ] 

def get_short_version(version):
    return re.findall("\d.\d+", version)[0]

def print_short_versions():
    for version in diff_versions_short():
        print(version)

if __name__ == "__main__":
    for version in diff_versions():
        print(version)