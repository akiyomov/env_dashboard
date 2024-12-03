const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
    const baseUrl = 'http://localhost:8000'; 
    const loginUrl = `${baseUrl}/admin/login/`; 
    const adminUsername = 'asadbey';
    const adminPassword = 'asadbey';
    const urls = [
        '/',
        '/queries/',
        '/locations/',
        '/locations/create/',
        '/metrics/',
        '/metrics/create/',
        '/alerts/',
        '/alerts/create/',
        '/aqi/',
        '/aqi/create/'
    ];

    const outputDir = './pdfs';

    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir);
    }

    const browser = await puppeteer.launch({
        headless: false, 
        args: ['--start-fullscreen'] 
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 }); 

    console.log(`Logging in to ${loginUrl}`);
    await page.goto(loginUrl, { waitUntil: 'networkidle2' });
    await page.type('#id_username', adminUsername); 
    await page.type('#id_password', adminPassword); 
    await Promise.all([
        page.click('input[type="submit"]'), 
        page.waitForNavigation({ waitUntil: 'networkidle2' }) 
    ]);

    console.log('Login successful!');

    for (const url of urls) {
        const fullUrl = `${baseUrl}${url}`;
        console.log(`Processing: ${fullUrl}`);
        await page.goto(fullUrl, { waitUntil: 'networkidle2' });

        const filename = url === '/' ? 'home.pdf' : `${url.replace(/\//g, '_')}.pdf`;
        const filePath = `${outputDir}/${filename}`;

        await page.pdf({
            path: filePath,
            format: 'A4',
            landscape: true, 
            printBackground: true 
        });
        console.log(`Saved PDF: ${filePath}`);
    }

    await browser.close();
})();
