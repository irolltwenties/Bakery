import asyncio
import json
import websockets
from pandas import Series
from pandas_ta import rsi


async def candlestick_binance(uri='wss://stream.binance.com:9443/ws/btcusdt@kline_5m', length=15):
    """Fetches data from Binance kline stream and calculate RSi coef from gathered data
    :param uri: str URI to connect to binance kline stream
    :param length: int length of calculating RSI (if needed 14, then length=15)
    """
    
    close_list = []
    async with websockets.connect(uri) as web_socket:
        while True:
            response = await web_socket.recv()
            data = json.loads(response)['k']
            is_closed = data['x']

            if is_closed:
                close_price = float(data['c'])
                close_list.append(close_price)

                if len(close_list) > length:
                    close_list.pop(0)

                if len(close_list) == length:
                    result = rsi(Series(close_list), length=length-1).tail(1).values
                    print(
                        f'Binance local RSI == {round(result[0], 4)}'
                        f'\nBinance close price == {close_price}'
                    )


async def candlestick_bitfinex(uri='wss://api-pub.bitfinex.com/ws/2',
                               request='{ "event": "subscribe",  "channel": "candles",  "key": "trade:1m:tBTCUSD" }'):
    """Fetches data from Bitfinex kline stream and calculates WVAP based on data gathered
    :param uri: str URI to connect to Bitfinex api pub
    :param request: dict of params to subscribe to current candle stream
    """
    
    async with websockets.connect(uri) as web_socket:
        await web_socket.send(request)
        cumulative_pv: float = 0
        cumulative_volume: float = 0
        while True:
            response = await web_socket.recv()
            data = json.loads(response)
            if isinstance(data, list) and data[1] != 'hb':
                try:
                    close_price = float(data[1][2])
                    max_price = float(data[1][3])
                    min_price = float(data[1][4])
                    volume = float(data[1][5])
                    cumulative_volume += volume
                    typical_price = (max_price + min_price + close_price) / 3
                    cumulative_pv += typical_price * volume
                    wvap = cumulative_pv / cumulative_volume
                    print(
                        f'Bitfinex close price == {close_price}'
                        f'\nBitfinex WVAP == {round(wvap, 3)}'
                    )
                except TypeError:
                    pass


async def main():
    async with asyncio.TaskGroup() as tg:
        task_binance = tg.create_task(candlestick_binance())
        task_bitfinex = tg.create_task(candlestick_bitfinex())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('This is the end.')