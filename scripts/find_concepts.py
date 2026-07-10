"""Find correct concept board names in akshare."""
import akshare as ak
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = ak.stock_board_concept_name_em()
print(f'Total concepts: {len(df)}')

keywords = ['航天', '军工', '黄金', '券商', '水利', 'AI', '人工', '机器人', '旅游', '航运', '石油', '保险', '水泥', '光伏', '储能', '半导体']

for keyword in keywords:
    matches = df[df['板块名称'].str.contains(keyword, na=False)]
    if len(matches) > 0:
        print(f'\n{keyword}:')
        for _, row in matches.head(3).iterrows():
            print(f'  - {row["板块名称"]}')
