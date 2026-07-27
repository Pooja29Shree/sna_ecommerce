import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from data_exporter import export_network

# Common user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

def extract_asin_from_url(url):
    # Match /dp/ASIN or /product/ASIN
    match = re.search(r'/(?:dp|product|ASIN)/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    return None

def parse_product_page(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Product ID (ASIN)
    asin = extract_asin_from_url(url)
    if not asin:
        # try hidden input
        asin_input = soup.find('input', {'id': 'ASIN'})
        if asin_input:
            asin = asin_input.get('value')
    
    if not asin:
        return None, []

    # 2. Product Name
    product_name = ""
    title_el = soup.find(id='productTitle')
    if title_el:
        product_name = title_el.get_text(strip=True)
        
    # 3. Category
    category = ""
    breadcrumb = soup.find(id='wayfinding-breadcrumbs_container')
    if breadcrumb:
        crumbs = breadcrumb.find_all('a', class_='a-link-normal')
        if crumbs:
            category = " > ".join([c.get_text(strip=True) for c in crumbs])

    node = {
        'Product ID': asin,
        'Product Name': product_name,
        'Category': category
    }

    # 4. Recommendations
    edges = []
    # Amazon has various carousel classes for recommendations. E.g. 'a-carousel-card'
    carousel_cards = soup.find_all('li', class_='a-carousel-card')
    for card in carousel_cards:
        link = card.find('a', class_='a-link-normal')
        if link and link.has_attr('href'):
            rec_url = link['href']
            rec_asin = extract_asin_from_url(rec_url)
            if rec_asin and rec_asin != asin:
                edges.append({
                    'Source Product ID': asin,
                    'Target Product ID': rec_asin
                })
                
    return node, edges


async def run_scraper(start_asin, max_products=5):
    nodes = []
    edges = []
    
    visited = set()
    queue = [start_asin]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()
        
        while queue and len(visited) < max_products:
            current_asin = queue.pop(0)
            if current_asin in visited:
                continue
                
            print(f"Scraping ASIN: {current_asin} ({len(visited)+1}/{max_products})")
            visited.add(current_asin)
            
            url = f"https://www.amazon.com/dp/{current_asin}"
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                # Wait for potential carousels to load
                try:
                    await page.wait_for_selector('.a-carousel-card', timeout=5000)
                except Exception:
                    pass # Carousel might not exist
                    
                html = await page.content()
                
                node, new_edges = parse_product_page(html, url)
                if node:
                    nodes.append(node)
                    edges.extend(new_edges)
                    
                    for edge in new_edges:
                        if edge['Target Product ID'] not in visited and edge['Target Product ID'] not in queue:
                            queue.append(edge['Target Product ID'])
                            
            except Exception as e:
                print(f"Failed to scrape {current_asin}: {e}")
                
            await asyncio.sleep(2) # delay to be nice
            
        await browser.close()
        
    export_network(nodes, edges)


if __name__ == "__main__":
    # Example ASIN to start with (e.g. some popular product like a kindle or echo)
    # Echo Dot 5th Gen: B09B8V1LZ3
    start_product_asin = "B09B8V1LZ3"
    print(f"Starting crawl from ASIN: {start_product_asin}")
    asyncio.run(run_scraper(start_product_asin, max_products=2))
