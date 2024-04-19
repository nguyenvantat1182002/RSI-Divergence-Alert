from binance.um_futures import UMFutures
from typing import List


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


def get_pairs(client: UMFutures) -> List[str]:
    info = client.exchange_info()
    symbols = list(filter(lambda x: x['contractType'] == 'PERPETUAL', info['symbols']))
    return [(item['pair'], item['underlyingSubType'][0].lower()) for item in symbols if item['pair'].endswith('USDT') and item['underlyingSubType']]


client = UMFutures()
pairs = get_pairs(client)
res: set = set()

for pair, categories in pairs:
    if not categories:
        continue
    res.add(categories.lower())

print(res)


