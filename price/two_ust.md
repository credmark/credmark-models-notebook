ax = plt.gca()

pp_univ3 = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).uniswap_v3.get_weighted_price(Token('UST'))['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_univ3, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)

pp_univ2 = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).uniswap_v2.get_weighted_price(Token('UST'))['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_univ2, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)

pp_sushi = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).sushiswap.get_weighted_price(Token('UST'))['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_sushi, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)

pp_all = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).price.dex_blended(Token('UST'))['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_all, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)
ax.legend(['univ3-ust-wormhole','univ2-ust-wormhole', 'sushi-ust-wormhole', 'all-ust-wormhole'])

# plt.show()

ax = plt.gca()

pp_univ3 = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).uniswap_v3.get_weighted_price(Token('UST (Wormhole)'))['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_univ3, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)

pp_sushi = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).sushiswap.get_weighted_price(Token('UST (Wormhole)'))['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_sushi, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)

pp_all = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).price.dex_blended(Token('UST (Wormhole)'))['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_all, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)

pp_all = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).price.dex_blended_tokens(tokens=[Token('UST')])['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_all, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)

pp_all = (lambda models=models: [ (14841257-x, BlockNumber(14841257-x).timestamp_datetime, models(block_number=14841257-x,local=True).price.dex_blended_tokens(tokens=[Token('UST'), Token('UST (Wormhole)')])['price']) for x in range(0, 140000, 1000)])()
pd.DataFrame(pp_all, columns=['block_number', 'Date', "price"]).plot('Date', 'price', ax=ax)

ax.legend(['univ3-ust-wormhole', 'sushi-ust-wormhole', 'ust-wormhole', 'two-ust'])
