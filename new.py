import asyncio
from pyppeteer import launch

async def generate_pdf(url, output_file):
    browser = await launch(executablePath='C:\\Users\\DlN\\AppData\\Local\\Chromium\\Application\\chrome.exe')
    page = await browser.newPage()
    
    # Emulate mobile device
    await page.emulate({
        'name': 'iPhone X',
        'userAgent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'viewport': {
            'width': 375,
            'height': 812,
            'deviceScaleFactor': 3,
            'isMobile': True,
            'hasTouch': True,
            'isLandscape': False
        }
    })
    
    await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 60000})
    await page.pdf({'path': output_file, 'format': 'A2'})
    await browser.close()

url = input("Enter the URL of the webpage: ")
output_file = input("Enter the desired output PDF file path: ")

asyncio.get_event_loop().run_until_complete(generate_pdf(url, output_file))
