import os 
from helpers.scraper import Scraper
from bs4 import BeautifulSoup
from tqdm import tqdm

image_folders = os.listdir('./output')

scraper = Scraper('https://wms.lroc.asu.edu/lroc/view_lroc/LRO-L-LROC-2-EDR-V1.0/M116180932ME')

extracting_fields = ['Resolution', 'Upper right latitude', 'Upper right longitude', 'Lower right latitude', 'Lower right longitude', 'Upper left latitude', 'Upper left longitude', 'Lower left latitude', 'Lower left longitude']


for image_name in tqdm(image_folders):
    scraper.get(f'https://wms.lroc.asu.edu/lroc/view_lroc/LRO-L-LROC-2-EDR-V1.0/{image_name}')
    
    soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')
    
    info = {}
    
    table_rows = soup.find_all('tr')
    for row in table_rows:
        cells = row.find_all('td')
        if len(cells) == 2:  # Ensure we have a key-value pair
            key = cells[0].text.strip()
            value = cells[1].text.strip()
            if key in extracting_fields:
                info[key] = value
                
    # save to json 
    with open(f'./output/{image_name}/info.json', 'w') as f:
        f.write(str(info))
