import json
import os
import urllib.request
import urllib.parse
from PIL import Image

def fetch_image_url(query):
    # Simple search via duckduckgo html or wikimedia to avoid complex JS scraping
    # We'll use Wikimedia Commons API as it's open, or DuckDuckGo HTML
    import json
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        # Try Wikimedia API first for high quality free images
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, context=ctx).read()
        data = json.loads(res.decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            if 'original' in page_data:
                return page_data['original']['source']
    except Exception as e:
        print(f"Wikimedia failed for {query}: {e}")
        pass

    try:
        # Fallback to duckduckgo lite
        url = f"https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({'q': query + " photo"}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
        # Very rudimentary extraction
        if "src=\"//external-content.duckduckgo.com/iu/" in res:
            part = res.split("src=\"//external-content.duckduckgo.com/iu/?u=")[1]
            img_url = part.split("\"")[0]
            return urllib.parse.unquote(img_url)
    except Exception as e:
        print(f"DDG failed for {query}: {e}")
    return None

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

with open('static/events_gallery.json', 'r') as f:
    events = json.load(f)

os.makedirs('static/images/events/scraped', exist_ok=True)

for ev in events['events']:
    img_path = ev.get('image', '')
    # If it's a generic icon or a reused generic image (like tangier.jpg for everything)
    is_generic = img_path in ['/static/icons/icon-512.png', '/static/images/events/tangier.jpg', '/static/images/events/jazz.jpg', '/static/images/events/biennale.jpg', '/static/images/events/eid.jpg', '/static/images/events/surf.jpg']
    
    # Keep the ones we explicitly generated or manually assigned successfully
    is_safe = "tap_in_soiree" in img_path or "gnaoua" in img_path or "rose" in img_path or "mawazine" in img_path or "fes" in img_path or "chefchaouen" in img_path
    
    if is_generic and not is_safe:
        query = ev['title']
        print(f"Searching for: {query}")
        img_url = fetch_image_url(query + " Morocco")
        
        if img_url:
            print(f"  Found: {img_url}")
            try:
                # Download
                filename = f"static/images/events/scraped/{ev['id']}.jpg"
                req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, context=ctx, timeout=10) as response, open(filename, 'wb') as out_file:
                    out_file.write(response.read())
                
                # Crop square
                with Image.open(filename) as img:
                    img = img.convert('RGB') # remove alpha if png
                    sq = crop_max_square(img)
                    sq = sq.resize((600, 600), Image.Resampling.LANCZOS)
                    sq.save(filename, quality=85)
                    
                ev['image'] = f"/{filename}"
                print(f"  Saved and cropped successfully.")
            except Exception as e:
                print(f"  Error processing image: {e}")
        else:
            print("  No image found.")

with open('static/events_gallery.json', 'w') as f:
    json.dump(events, f, indent=2)

print("Done scraping!")
