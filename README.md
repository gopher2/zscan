# ZSCAN

zscan is a python / sql wrapper around the zmap program to map your network and find and alert on new open services.

## Installation

Only dependencies are python3 and zmap. 

```bash
sudo apt-get install zmap python3
git clone https://github.com/gopher2/zscan
```

## Usage

You will need to run as root as zmap requires it
```bash
cd zscan
sudo python ./zscan.py
```

## License
[GPL3](https://www.gnu.org/licenses/gpl-3.0.txt)
