from scraper import Scraper
import sys
import time

scraper = Scraper('https://wms.lroc.asu.edu/lroc/search')
time.sleep(5)

def main(img_name: str):
    scraper.element_send_keys('input[name="filter[product_id]"]', img_name)
    scraper.element_click('input[type="submit"]')
    scraper.find_element_by_xpath('//a[contains(text(), "M119415370ME")]').click()
    scraper.find_element_by_xpath('//a[contains(text(), "Download EDR")]').click()
    time.sleep(5)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python download.py <image_name>")
        sys.exit(1)

    img_name = sys.argv[1]
    main(img_name)