import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urlparse

def get_product_id(url):
    # e.g., https://scrapeme.live/shop/bulbasaur/ -> bulbasaur
    path = urlparse(url).path
    return path.strip('/').split('/')[-1]

def scrape_pokemon_network(start_url, max_pages=50):
    nodes = []
    edges = []
    
    visited = set()
    queue = [start_url]
    
    print(f"Starting real scrape from {start_url}")
    
    while queue and len(visited) < max_pages:
        current_url = queue.pop(0)
        prod_id = get_product_id(current_url)
        
        if prod_id in visited:
            continue
            
        print(f"Scraping [{len(visited)+1}/{max_pages}]: {prod_id}")
        visited.add(prod_id)
        
        try:
            # Using simple requests and BeautifulSoup as requested
            r = requests.get(current_url, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200:
                print(f"Failed to fetch {current_url}: HTTP {r.status_code}")
                continue
                
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract product details
            title_el = soup.find('h1', class_='product_title')
            name = title_el.text.strip() if title_el else prod_id
            
            price_el = soup.find('p', class_='price')
            price = price_el.text.strip() if price_el else ""
            
            cat_el = soup.select('span.posted_in a')
            category = cat_el[0].text.strip() if cat_el else "Unknown"
            
            # Extract recommendations (Related products)
            recommended_urls = [a['href'] for a in soup.select('section.related.products a.woocommerce-LoopProduct-link')]
            rec_ids = [get_product_id(u) for u in recommended_urls]
            
            nodes.append({
                'Product ID': prod_id,
                'Product Name': name,
                'Category': category,
                'Price': price,
                'Recommended product IDs': ",".join(rec_ids)
            })
            
            for rec_id, rec_url in zip(rec_ids, recommended_urls):
                edges.append({
                    'Source Product ID': prod_id,
                    'Target Product ID': rec_id
                })
                # Queue the recommended product to build the network
                if rec_id not in visited and rec_url not in queue:
                    queue.append(rec_url)
                    
            # Small delay to be polite
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error scraping {current_url}: {e}")
            
    # Export datasets
    df_nodes = pd.DataFrame(nodes)
    df_edges = pd.DataFrame(edges)
    
    df_nodes.to_csv('scraped_nodes.csv', index=False)
    df_edges.to_csv('scraped_edges.csv', index=False)
    
    print("\nScraping finished!")
    print(f"Saved {len(df_nodes)} nodes to scraped_nodes.csv")
    print(f"Saved {len(df_edges)} edges to scraped_edges.csv")

if __name__ == "__main__":
    start_url = "https://scrapeme.live/shop/bulbasaur/"
    scrape_pokemon_network(start_url, max_pages=150)
