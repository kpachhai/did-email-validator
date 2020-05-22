# DID Email Validator for Vouch

To start, clone vouch-restapi-backend repo
```
git clone https://github.com/tuum-tech/did-email-validaor.git;
cd vouch-restapi-backend;
```
# Prerequisites
- Python3 is needed
```
brew install python3 // On Mac
sudo apt-get install python3 // On linux
```
- Virtualenv
```
pip3 install virtualenv
```

# Setup
Before you start, you have to initiate vouch-redis-broker https://github.com/tuum-tech/vouch-redis-broker
- Create a python virtual environment
```
virtualenv -p `which python3` venv
```
- Activate the virtualenv environment
```
source venv/bin/activate
```
- Install the dependencies
```
pip install -r requirements.txt
```

# Run
- Start DID Validator service
```
python emailValidator.py
```