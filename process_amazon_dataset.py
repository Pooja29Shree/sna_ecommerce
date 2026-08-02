"""
Amazon Video Games Recommendation Network Dataset Builder
=========================================================
Source   : Stanford SNAP - Amazon Product Data (2014)
URL      : https://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Video_Games.json.gz
Method   : Parsed directly from the gzipped JSON metadata file using Python's gzip + ast.literal_eval
Fields   : asin (Product ID), title, price, categories, related['also_bought'] (recommendations)

Output:
  amazon_nodes.csv  - Products (nodes) with ID, Name, Category, Price, Recommended IDs
  amazon_edges.csv  - Directed recommendation links (Source Product -> Target Product)
"""

import gzip
import ast
import pandas as pd
import re

INPUT_FILE = 'meta_Video_Games.json.gz'
NODES_FILE = 'amazon_nodes.csv'
EDGES_FILE = 'amazon_edges.csv'

def clean_text(text):
    """Strip HTML tags and normalize whitespace."""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', str(text))
    return ' '.join(text.split())[:120]

def build_network():
    nodes = []
    edges = []

    print(f"Reading: {INPUT_FILE}")
    print(f"Source : Stanford SNAP (Amazon Product Metadata 2014)\n")

    with gzip.open(INPUT_FILE, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                item = ast.literal_eval(line)
            except Exception:
                continue

            asin     = item.get('asin', '').strip()
            title    = clean_text(item.get('title', ''))
            price    = item.get('price', '')

            # Category: take the deepest sub-category from first list
            cats     = item.get('categories', [])
            category = cats[0][-1] if cats and cats[0] else 'Unknown'

            # Recommendation edges: "also_bought" = the network we need
            related       = item.get('related', {})
            also_bought   = related.get('also_bought', [])

            if not asin:
                continue

            nodes.append({
                'Product ID'             : asin,
                'Product Name'           : title,
                'Category'               : category,
                'Price (USD)'            : price,
                'Recommended product IDs': ','.join(also_bought)
            })

            for target in also_bought:
                edges.append({
                    'Source Product ID': asin,
                    'Target Product ID': target,
                    'Type'             : 'Directed'
                })

            if (i + 1) % 10000 == 0:
                print(f"  Processed {i+1:,} records | Nodes: {len(nodes):,} | Edges: {len(edges):,}")

    print(f"\nTotal records processed : {len(nodes):,}")
    print(f"Total recommendation edges: {len(edges):,}")

    # Build DataFrames
    df_nodes = pd.DataFrame(nodes).drop_duplicates(subset=['Product ID'])
    df_edges = pd.DataFrame(edges).drop_duplicates()

    # Save
    df_nodes.to_csv(NODES_FILE, index=False)
    df_edges.to_csv(EDGES_FILE, index=False)

    print(f"\n[DONE] Saved {len(df_nodes):,} nodes  -->  {NODES_FILE}")
    print(f"[DONE] Saved {len(df_edges):,} edges  -->  {EDGES_FILE}")
    print("\nDataset is ready for network analysis!")
    print("Use these files in Gephi or Python (networkx) to calculate:")
    print("  - Average Clustering Coefficient (AvgCC)")
    print("  - PageRank Variance (PRVar)")
    print("  - Network Size, Density, etc.")

if __name__ == "__main__":
    build_network()
