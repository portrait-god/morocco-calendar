import json
import os
import urllib.request
import urllib.parse
from PIL import Image

def fetch_image_wikimedia(query):
    query_str = urllib.parse.quote(query)
    # Search Wikimedia Commons for pages matching the query
    url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={query_str}&gsrnamespace=6&prop=imageinfo&iiprop=url&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'MoroccoApp Scraper (shanemccormick@Shanes-MacBook-Pro.local)'})
    
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        res = urllib.request.urlopen(req, context=ctx).read()
        data = json.loads(res.decode('utf-8'))
        
        # Check if we got results
        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']
            # Get the first image result's URL
            for page_id in pages:
                page = pages[page_id]
                if 'imageinfo' in page and len(page['imageinfo']) > 0:
                    img_url = page['imageinfo'][0]['url']
                    if not img_url.endswith('.svg') and not img_url.endswith('.pdf'):
                        return img_url
    except Exception as e:
        print(f"  Wikimedia failed: {e}")
    return None

def crop_max_square(pil_img):
    img_width, img_height = pil_img.size
    crop_size = min(img_width, img_height)
    return pil_img.crop(((img_width - crop_size) // 2,
                         (img_height - crop_size) // 2,
                         (img_width + crop_size) // 2,
                         (img_height + crop_size) // 2))

with open('static/events_gallery.json', 'r') as f:
    events = json.load(f)

for ev in events['events']:
    img_path = ev.get('image', '')
    
    is_generic = img_path in [
        '/static/icons/icon-512.png', 
        '/static/images/events/tangier.jpg', 
        '/static/images/events/jazz.jpg', 
        '/static/images/events/biennale.jpg', 
        '/static/images/events/eid.jpg', 
        '/static/images/events/surf.jpg',
        '/static/images/events/rose.jpg'
    ]
    
    if "tap_in_soiree" in img_path or "fes" in img_path or "chefchaouen" in img_path or "eid" in ev['title'].lower() or "biennale" in ev['title'].lower() or "rose" in ev['title'].lower() or "mawazine" in ev['title'].lower():
        continue
        
    if is_generic:
        # Simplify query to get better Wikimedia hits
        query_terms = [word for word in ev['title'].split() if len(word) > 3 and word.lower() not in ['festival', 'preview', 'weekend', 'opening']]
        query = " ".join(query_terms) + ' Morocco'
        
        print(f"Searching for: {query}")
        img_url = fetch_image_wikimedia(query)
        
        if img_url:
            print(f"  Found: {img_url[:60]}...")
            try:
                filename = f"static/images/events/scraped/{ev['id']}.jpg"
                req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, context=ctx, timeout=10) as response, open(filename, 'wb') as out_file:
                    out_file.write(response.read())
                
                with Image.open(filename) as img:
                    img = img.convert('RGB')
                    sq = crop_max_square(img)
                    sq = sq.resize((600, 600), Image.Resampling.LANCZOS)
                    sq.save(filename, quality=85)
                    
                ev['image'] = f"/{filename}"
                print(f"  Saved.")
            except Exception as e:
                print(f"  Error mapping image: {e}")
        else:
            print("  No image found.")

with open('static/events_gallery.json', 'w') as f:
    json.dump(events, f, indent=2)

print("Done scraping round 3 via Wikimedia Commons!")
