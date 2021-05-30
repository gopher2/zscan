# ZSCAN

zscan is a python / sql wrapper around the zmap program to map your network and find and alert on new open services.

## Installation

Only dependencies are python system and zmap. 

```bash
sudo apt-get install zmap python3 python3-pip python3-venv
git clone https://github.com/gopher2/zscan
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 ./zscan.py reset
python3 -m flask run
```

## Usage

Scans are manually initiated right now, You will need to run as root as zmap requires it
```bash
cd zscan
sudo python ./zscan.py
```
Point your web browser at http://localhost:5000 to view the results

You can wipe out the database and initalize with default values with the reset argument
```bash
python ./zscan.py reset
```

## License
[GPL3](https://www.gnu.org/licenses/gpl-3.0.txt)
