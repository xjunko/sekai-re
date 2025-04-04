# sekai-re.py
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


project sekai files reverse engineering

## requirements
- [uv](https://github.com/astral-sh/uv) to run the project

## disclaimer
to use this project, you first have to fetch the files from it's source.
one of the ways you can do this are with [sssekai](https://github.com/mos9527/sssekai).

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
### getting raw score (.sus) files and it's files
``` bash
sekai-re.py extract_music --in "/SekaiRE/root/" --out "/SekaiRE/out/"
```
#### results
![image](https://github.com/user-attachments/assets/e49bb3de-1c57-4467-8d58-610be6f908a8)
<img src="https://github.com/user-attachments/assets/256355f3-d0df-4b60-ac30-ffe606a7275d" height="300px">
<img src="https://github.com/user-attachments/assets/03fe7589-6e9f-47ab-bf9e-e7ac433a8c81" height="300px">
* with this you can natively load the files in another programs.

# credits
* [UnityPy](https://github.com/K0lb3/UnityPy)
* [sssekai](https://github.com/mos9527/sssekai)
