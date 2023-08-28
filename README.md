# Project Description
This script performs connections to Binance and Bitfinex WebSocket API, listens to data and calculating RSI from Binance data, and calculating WVAP from Bitfinex data.
## Usage
To use this script, you need to run main.py, which defines the main() function, containing two asyncio tasks. 

```python main.py```

Then, you would receive WVAP from Bitfinex first and wait some time to start receiving data from Binance. 
You will start to receive RSI values after the function would gather enough candles.
## Installation
```
pip install -r requirements.txt
```
<hr>
Requires Python v 3.11
