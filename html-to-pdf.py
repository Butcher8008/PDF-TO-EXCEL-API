from flask import Flask, jsonify, request
import asyncio
from pyppeteer import launch

app = Flask(__name__)

# Launch browser instance outside of coroutine function
browser = None

async def generate_pdf(url, output_file, view='desktop'):
    global browser  # Access the browser instance defined outside this function
    if browser is None:
        # Launch browser only if not already launched
        browser = await launch(executablePath='C:\\Users\\DlN\\AppData\\Local\\Chromium\\Application\\chrome.exe')
    page = await browser.newPage()
    if view == 'mobile':
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
    await page.pdf({'path': output_file, 'format': 'A4' if view == 'mobile' else 'A0'})

@app.route('/generate-pdf', methods=['POST'])
async def generate_pdf_from_url():
    data = request.get_json()
    url = data.get('url')
    output_file = data.get('output_file')
    view = data.get('view', 'desktop')
    
    await generate_pdf(url, output_file, view)
    
    return jsonify({'message': 'PDF generated successfully'})

if __name__ == '__main__':
    app.run(debug=True)
