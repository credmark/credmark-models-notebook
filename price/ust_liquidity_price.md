context.reset_cache('tmp/ust_in_may.sqlite')

liquidity_all = (lambda models=models:
 [ (14841257-x,

    BlockNumber(14841257-x).timestamp_datetime,

    (models(14841257-x).price.dex_pool(symbol='UST (Wormhole)', local=True, return_type=Some).to_dataframe()),

    (models(14841257-x).price.dex_pool(symbol='USDC', local=True, return_type=Some).to_dataframe()),

    (models(14841257-x).price.dex_pool(symbol='USDT', local=True, return_type=Some).to_dataframe()),

    (models(14841257-x).price.dex_pool(symbol='DAI', local=True, return_type=Some).to_dataframe()),

    models(block_number=14841257-x, local=True).price.dex_blended(Token('UST (Wormhole)'))['price']
   )
   for x in range(0, 140000, 1000) ])()

liquidity_all = [
(block_number,
 block_time,
 price,

df.assign(tick_liquidity_t=lambda x, input_address=Token('UST (Wormhole)').address: x.one_tick_liquidity0.where(x.token0_address == input_address, x.one_tick_liquidity1)).tick_liquidity_t.sum(),

df.query('src == "uniswap-v3.get-weighted-price"').assign(tick_liquidity_t=lambda x, input_address=Token('UST (Wormhole)').address: x.one_tick_liquidity0.where(x.token0_address == input_address, x.one_tick_liquidity1)).tick_liquidity_t.sum(),

df.query('src != "uniswap-v3.get-weighted-price"').assign(tick_liquidity_t=lambda x, input_address=Token('UST (Wormhole)').address: x.one_tick_liquidity0.where(x.token0_address == input_address, x.one_tick_liquidity1)).tick_liquidity_t.sum(),

df.query('src != "uniswap-v3.get-weighted-price"').assign(full_liquidity_t=lambda x, input_address=Token('UST (Wormhole)').address: x.full_tick_liquidity0.where(x.token0_address == input_address, x.full_tick_liquidity1)).full_liquidity_t.sum(),

df2.assign(tick_liquidity_t=lambda x, input_address=Token('USDC').address: x.one_tick_liquidity0.where(x.token0_address == input_address, x.one_tick_liquidity1)).tick_liquidity_t.sum(),

df3.assign(tick_liquidity_t=lambda x, input_address=Token('USDT').address: x.one_tick_liquidity0.where(x.token0_address == input_address, x.one_tick_liquidity1)).tick_liquidity_t.sum(),

df4.assign(tick_liquidity_t=lambda x, input_address=Token('DAI').address: x.one_tick_liquidity0.where(x.token0_address == input_address, x.one_tick_liquidity1)).tick_liquidity_t.sum(),

     )
for block_number, block_time, df, df2, df3, df4, price in liquidity_all
]

99000

df = pd.DataFrame(liquidity_all, columns = ['block_number', 'Block time', 'price', '1-tick liquidity (UniV2+V3)', '(UniV3)', '(UniV2)', '(UniV2) Full', 'USDC (UniV2+V3)', 'USDT (UniV2+V3)', 'DAI (UniV2+V3)'])

ax = plt.gca()
df.plot('Block time', ['price', '1-tick liquidity (UniV2+V3)', '(UniV2)', '(UniV3)', 'USDC (UniV2+V3)', 'USDT (UniV2+V3)', 'DAI (UniV2+V3)'], ax=ax, subplots=True, title='UST (Wormhole) Price vs Liquidity (May-2022)', sharex=True)

ax.set_xlabel("Block time")
ax.set_ylabel("Price ($)")
plt.show()
