import pandas as pd

nodes = pd.read_csv('amazon_nodes.csv')
edges = pd.read_csv('amazon_edges.csv')

print('=== FINAL DATASET SUMMARY ===')
print('Source   : Stanford SNAP - Amazon Product Data (2014)')
print('Category : Video Games')
print('URL      : https://snap.stanford.edu/data/amazon/productGraph/')
print()
print(f'Total Nodes (Products) : {len(nodes):,}')
print(f'Total Edges (Links)    : {len(edges):,}')
print(f'Nodes with a title     : {nodes["Product Name"].notna().sum():,}')
price_col = [c for c in nodes.columns if 'Price' in c][0]
print(f'Nodes with a price     : {nodes[price_col].notna().sum():,}')
print(f'Nodes with recs        : {nodes["Recommended product IDs"].notna().sum():,}')
print()
print('Sample Nodes:')
print(nodes[nodes["Product Name"].notna()].head(3)[['Product ID','Product Name','Category']].to_string())
print()
print('Sample Edges:')
print(edges.head(5).to_string())
