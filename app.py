import time
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import os

from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime, timedelta
from rsi_divergence_finder import RSIDivergenceFinder, DivergenceState
from binance.um_futures import UMFutures
from typing import List, Dict


HOOK_LINKS = {
    'btc': 'https://discord.com/api/webhooks/1230390062831898634/gZ1H4yblRCaDsId_hx7tBl0hDVi61z7aiu1PedcnqPQwUIWg8vFwDRwdx9v3VQcIuTMX',
    'nft': 'https://discord.com/api/webhooks/1230390714987319337/pwimkRLH1Uxh4poKwSFJgc-4xOO0ml2jfHERJluSqNalzP_rfxGQC0IJoHYcnqbh_-Pj',
    'cex': 'https://discord.com/api/webhooks/1230390748998795314/Xgth077t9SjCO-a1g4hsirLyUvZk5-AsoM6Qpa78BMrfigp6IJW58mEN-wFzzh4IHoS4',
    'privacy': 'https://discord.com/api/webhooks/1230390599597817916/grlOHyUfhhTdWzU2_q0AlVpQwhVDehdXEtlM7y7RTz2AswTc7w68wywcHz97_xjD64ce',
    'infrastructure': 'https://discord.com/api/webhooks/1230390221636370533/H1q89j8oHMHSnmMIdAukSUPmAM9mQpN0TIf6T8VHupe1VzZuga-UWCiUbswG-qjd3x1P',
    'metaverse': 'https://discord.com/api/webhooks/1230390423521071154/YMLn3PTXgErnLv4ilXSvg8BNEsdo8--aXaKNsBTQ8mMbWQzfBvky5V_Rr9bOZqyjKo2Y',
    'storage': 'https://discord.com/api/webhooks/1230390635840802816/kJI7yfTjGVGu7k2mggeWY_IA7rp6qt-VQtxGUgXqxSPwCjCRdDRNORMg-sRGdjEtW2FC',
    'dao': 'https://discord.com/api/webhooks/1230390801876652103/oXmcz6Gw_nRuqFosZQUshXP1WRMormWARTrxDjP_LJRWj55Je6ofeCxWHcAWN7bwufdP',
    'ai': 'https://discord.com/api/webhooks/1230390872374247434/Q8hIBoifjEnrZ1A19xP1_4RRflwwPhe0Xy1ZiNq4K_FRNneQdAYntg5apC_-L1qxbELt',
    'layer-2': 'https://discord.com/api/webhooks/1230390313307213974/4nBbih7bY1-vxCKfIYlTRLZrms0_svcfwYoAIkw9u7jy7B9YWmf88wzkRp6Jtyrbac9F',
    'payment': 'https://discord.com/api/webhooks/1230390523764670475/KPq-Y4nLATJ7Ogd6Rkv5rJ6c0xG2xogMLAIKUiSXycqXIyKvBFeKFwS0jUt3ZAob8_1g',
    'oracle': 'https://discord.com/api/webhooks/1230390461995155466/tGrpuoP1Th-SLlO-29uxkv9GMQdMiYOwFKVtQq7930fnigEBeuGNK_-AoiD31WJfrSGN',
    'pow': 'https://discord.com/api/webhooks/1230390560574013482/UxI_2XQAInRfj8CiQWxWCMn998dnUF3SMCQBYybScL0HizlXohva2GNnwsj7Xn7tImQd',
    'meme': 'https://discord.com/api/webhooks/1230390382441791509/yDMLATR9oEHC6tY9ut7LJeSxmP1XiFvW0pW3QCS__mSKxDCU4tFI03tnLHhrIWmope6Y',
    'index': 'https://discord.com/api/webhooks/1230390956990402600/AlJbGyrepSCVSurBa2N3pyknZN6LE3om-j_208fEBuskhb7Cvnsr2h55S5XZR0LdQ3VT',
    'layer-1': 'https://discord.com/api/webhooks/1230390268658974760/9vMtU0_Cez95b8M3rLZ9fMsoZC94PhQZ6cZjr9rePrwl_8lgIoa0uQIsD3Z-gOutfFad',
    'bitcoin eco': 'https://discord.com/api/webhooks/1230391067099267072/nhXOF_2WVarkuR5YeCzVDmNcW5BLtFbEj6rCFimKKwOicbPIpV5pbGBQbhqkHZwJmXxn',
    'defi': 'https://discord.com/api/webhooks/1230391152709074994/FlpkYG0-8U87pHaU3pFdW-oD5KMbANMYZmF_8g5ffUcCydZB0fcnencyVdSlgv7uGAGY',
    'dex': 'https://discord.com/api/webhooks/1230390914627670018/b3365kBsvMQXIOKlyzZ2n3c6eqlDaoTEoQvFzEy3-0EMI5uLiGlVrX94pQg_KLXb1TA9'
}
TIMEFRAMES = ['5m', '15m', '1h', '4h', '1d']


def savefig(file_name: str,
            df: pd.DataFrame,
            state: DivergenceState,
            point_1: pd.Series,
            point_2: pd.Series,
            rsi_point_1: pd.Series,
            rsi_point_2: pd.Series):
    df = df.copy()
    df = df.set_index('Time')
    
    colors = None
    alines_price = None

    match state:
        case DivergenceState.BEARISH:
            colors = ['r', 'r']
            alines_price = [(point_1['Time'], point_1['High']), (point_2['Time'], point_2['High'])]
        case DivergenceState.BULLISH:
            colors = ['g', 'g']
            alines_price = [(point_1['Time'], point_1['Low']), (point_2['Time'], point_2['Low'])]
    
    alines_rsi = [(rsi_point_1['Time'], rsi_point_1['RSI']), (rsi_point_2['Time'], rsi_point_2['RSI'])]
    plots = [
        mpf.make_addplot(df['RSI'], panel=2, color='black', ylabel='RSI', fill_between=dict(y1=30, y2=30, color="gray")),
        mpf.make_addplot(df['RSI'], panel=2, color='black', ylabel='RSI', fill_between=dict(y1=70, y2=70, color="gray")),
    ]

    s = mpf.make_mpf_style(base_mpf_style='yahoo',rc={'grid.alpha':0})
    _, axs = mpf.plot(df, type='candle', style=s, volume=True, addplot=plots, alines=dict(alines=alines_price, colors=colors), returnfig=True)
    
    alines_rsi = mpf._utils._construct_aline_collections(dict(alines=alines_rsi, colors=colors), df.index)
    axs[4].add_collection(alines_rsi)

    plt.savefig(file_name, bbox_inches='tight')
    plt.close()


def get_pairs(client: UMFutures) -> List[str]:
    info = client.exchange_info()
    symbols = list(filter(lambda x: x['contractType'] == 'PERPETUAL', info['symbols']))
    return [(item['pair'], item['underlyingSubType'][0].lower()) for item in symbols if item['pair'].endswith('USDT') and item['underlyingSubType']]


client = UMFutures()
watchlist_tokens: Dict[str, Dict[str, datetime]] = {}
timedeltas = {
    '1m': timedelta(minutes=1),
    '5m': timedelta(minutes=5),
    '15m': timedelta(minutes=15),
    '1h': timedelta(hours=1),
    '4h': timedelta(hours=4),
    '1d': timedelta(days=1)
}

pairs = get_pairs(client)

while True:
    for pair, category in pairs:
        if not pair in watchlist_tokens:
            watchlist_tokens.update({pair: {}})

        for timeframe in TIMEFRAMES:
            if not timeframe in watchlist_tokens[pair] or (timeframe in watchlist_tokens[pair] and datetime.now() > watchlist_tokens[pair][timeframe]['next_signal_search_time']):
                finder = RSIDivergenceFinder(client, pair, timeframe)

                try:
                    df, state, point_1, point_2, rsi_point_1, rsi_point_2 = finder.find()
                    if not state == DivergenceState.UNKNOW:
                        mess = f'{state} {pair} {timeframe}'
                        color = None
                        description = None
                        match state:
                            case DivergenceState.BEARISH:
                                color = '0eb3434'
                                description = 'Bearish Divergence'
                                mess += f' {point_1["Time"]} {point_1["High"]} {point_2["Time"]} {point_2["High"]}'
                            case DivergenceState.BULLISH:
                                color = '059eb34'
                                description = 'Bullish Divergence'
                                mess += f' {point_1["Time"]} {point_1["Low"]} {point_2["Time"]} {point_2["Low"]}'
                        print(mess)

                        file_path = f'{os.getcwd()}\\{pair}_{timeframe}.png'
                        file_name = os.path.basename(file_path)
                        savefig(file_path, df, state, point_1, point_2, rsi_point_1, rsi_point_2)

                        with open(file_path, "rb") as f:
                            image = file=f.read()
                        os.remove(file_path)

                        content = f"{pair}: {timeframe} - {description}"
                        
                        webhook = DiscordWebhook(url=HOOK_LINKS[category], content=content)
                        webhook.add_file(file=image, filename=file_name)
                        response = webhook.execute()
                        if not response.status_code == 200:
                            print(response.text)
                            exit(1)

                        if pair == 'BTCUSDT':
                            webhook = DiscordWebhook(url=HOOK_LINKS['btc'], content=content)
                            webhook.add_file(file=image, filename=file_name)
                            response = webhook.execute()
                            if not response.status_code == 200:
                                print(response.text)
                                exit(1)
                except Exception:
                    pass
                finally:
                    watchlist_tokens[pair].update({
                        timeframe: {
                            'next_signal_search_time': datetime.now() + timedeltas[timeframe]
                        }
                    })

            time.sleep(0.5)

    time.sleep(1)
