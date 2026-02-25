from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
import os
import io
import urllib.parse
import urllib.request
import json
import ssl

options = Options()
options.add_argument('--headless=new')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

def crop_max_square(pil_img):
    img_width, img_height = pil_img.size
    crop_size = min(img_width, img_height)
    return pil_img.crop(((img_width - crop_size) // 2,
                         (img_height - crop_size) // 2,
                         (img_width + crop_size) // 2,
                         (img_height + crop_size) // 2))

def get_high_res_image(query, safe_name):
    print(f"Searching: {query}")
    try:
        url = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(query + ' Morocco high quality photography')}"
        driver.get(url)
        time.sleep(2)
        
        try:
            btn = driver.find_element(By.XPATH, "//button[.//div[text()='Accept all']]")
            btn.click()
            time.sleep(1)
        except:
            pass

        # Click the first image thumbnail to open the side panel
        first_thumbnail = driver.find_element(By.CSS_SELECTOR, "img.YQ4gaf")
        driver.execute_script("arguments[0].scrollIntoView();", first_thumbnail)
        first_thumbnail.click()
        time.sleep(2) # Wait for side panel to load
        
        # Get the high-res image from the side panel. It usually has class "sFlh5c pT0Scc iPVvYb"
        high_res_img = None
        try:
             # Look for the actual image in the preview pane
             elements = driver.find_elements(By.CSS_SELECTOR, "img.sFlh5c.pT0Scc.iPVvYb")
             for el in elements:
                 src = el.get_attribute('src')
                 if src and src.startswith('http') and not src.startswith('https://encrypted'):
                     high_res_img = src
                     break
        except:
             pass
             
        # Fallback 1: Try finding by looking at the parent container of the preview
        if not high_res_img:
            try:
                preview_panel = driver.find_element(By.CSS_SELECTOR, 'div[data-ved]') 
                imgs = preview_panel.find_elements(By.TAG_NAME, 'img')
                for img in imgs:
                    src = img.get_attribute('src')
                    if src and src.startswith('http') and not src.startswith('https://encrypted') and 'gstatic' not in src:
                        high_res_img = src
                        break
            except:
                pass
                
        if high_res_img:
            print(f"  Found high-res URL: {high_res_img[:60]}...")
            
            # Download it
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(high_res_img, headers={'User-Agent': 'Mozilla/5.0'})
            
            path = f"static/images/events/unique/{safe_name}.jpg"
            os.makedirs("static/images/events/unique", exist_ok=True)
            
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response, open(path, 'wb') as out_file:
                out_file.write(response.read())
                
            # Crop it
            with Image.open(path) as img:
                img = img.convert('RGB')
                sq = crop_max_square(img)
                sq = sq.resize((600, 600), Image.Resampling.LANCZOS)
                sq.save(path, quality=85)
                
            print(f"  Saved {path}")
            return f"/{path}"
        else:
            print("  Could not extract high-res URL from panel.")
            
            # Absolute fallback: Take a screenshot of the preview panel image element itself, which is higher res than the thumbnail
            try:
                preview_img_el = driver.find_elements(By.CSS_SELECTOR, "img.sFlh5c.pT0Scc.iPVvYb")[0]
                png = preview_img_el.screenshot_as_png
                img = Image.open(io.BytesIO(png))
                img = img.convert('RGB')
                sq = crop_max_square(img)
                sq = sq.resize((600, 600), Image.Resampling.LANCZOS)
                path = f"static/images/events/unique/{safe_name}.jpg"
                sq.save(path, quality=85)
                print(f"  Saved via panel screenshot fallback to {path}")
                return f"/{path}"
            except Exception as e:
                 print(f"  Fallback panel screenshot failed: {e}")
                 
            return None

    except Exception as e:
        print(f"Failed {safe_name}: {e}")
        return None

with open('static/events_gallery.json', 'r') as f:
    events = json.load(f)

# The list of events we just scraped that need higher quality
scraped_ids = [
    "tangier-medina-souk-2026", "grandsoccofridaymarket4", "marrakech-biennale-2026", 
    "tangierphotographydays7", "asilahmuralsfestivalwarmupexhibitions11", "ramadannightmarkettangier12", 
    "chefchaouenthursdaysouk15", "eidalfitrcelebrationsendoframadan17", "bouinaniamadrasaeveningopening19", 
    "eid-al-fitr-2026", "moulayidrissmoussemfez21", "sefroucherryfestivalpreview24", 
    "rabatspringfestivalchellahnights30", "jazzablanca-2026", "rabatskatecontesthassaniiboulevard33", 
    "mawazinefestivalprepartyrabat35", "mawazinefestivalrabat36", "fridaykasbahoudayasculturalevent38", 
    "essaouira-surf-comp-2026", "lboulevardfestivalurbanmusic44", "casablancastreetarttour51", 
    "essaouirabeachbonfiresurfsession57", "rose-festival-2026", "essaouirakitewindsurfcompetition61", 
    "gnaouafestivalwarmupconcertsessaouiraport64", "gnaouaworldmusicfestivalmainweekend65", "lblvd-2026", 
    "essaouirawednesdayartisanmarket68", "anchorpointsurfjam72", "rosefestivaldaytripelkelaamgouna79", 
    "jemaaelfnaastorytellershalqanight80", "tbouridahorsesshowrehearsalmarrakech82", 
    "marrakechbiennalemedinainstallations84", "ourikavalleyberberfestivalweekend86", 
    "marrakechmarathonweekendstreetfestival88", "nightmarketsendofseasonsouk89"
]

for ev in events['events']:
    if ev['id'] in scraped_ids:
        # Re-run the high res fetch
        res = get_high_res_image(ev['title'], ev['id'])
        if res:
            ev['image'] = res

with open('static/events_gallery.json', 'w') as f:
    json.dump(events, f, indent=2)

driver.quit()
print("High-res scraping complete!")
