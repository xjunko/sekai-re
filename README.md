# sekai-re.py
project sekai file reverse engineering

## requirements
- [uv](https://github.com/astral-sh/uv) to run the project

## usage
```
usage: sekai-re.py [-h] {extract_music} ...

Project Sekai reverse engineering suites

positional arguments:
  {extract_music}  Subcommands
    extract_music  Decrypt and extract music assets

options:
  -h, --help       show this help message and exit
```
### getting raw score (.sus) files and it's required files
``` bash
sekai-re.py extract_music --in "/SekaiRE/root/" --out "/SekaiRE/out/"
```