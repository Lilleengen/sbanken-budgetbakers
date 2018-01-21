# sbanken-budgetbakers
Python script to import Sbanken transactions in to Budget Bakers Wallet.

## Advice
As this is accessing your bank account, you shuld __always read the code before running it__. If you don't understand it, __do not run it!__

## Usage
```bash
❯ ./sbanken-budgetbakers.py
```

## Installation
If you don't already have it installed, install Python 3 and pip3

```bash
pip3 install -r requirements.txt
mv config.json.example config.json
nano config.json # Configure Sbanken and Budget Bakers API
chmod +x sbanken-cli.py
```
