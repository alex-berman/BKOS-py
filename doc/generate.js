const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  const dialogDir = path.join(__dirname, 'dialogs');
  const files = fs.readdirSync(dialogDir).filter(file => file.endsWith('.txt'));

  for (let file of files) {
    const filePath = path.join(dialogDir, file);
    const dialogContent = fs.readFileSync(filePath, 'utf-8').split('\n');

    let htmlContent = `
      <html>
      <head>
        <link rel="stylesheet" href="styles.css">
      </head>
      <body>
      <div class="container">`;

    for (let line of dialogContent) {
      const parts = line.split(':');
      if (parts.length < 2) {
        htmlContent += '<div class="spacing"></div>';
      }
      else {
        const [speaker, message] = parts.map(str => str.trim());
        if (speaker === 'S') {
          htmlContent += `
            <div class="utterance_container_S">
              <div class="utterance_bubble background_S">
                <div class="utterance">${message}</div>
              </div>
            </div>`;
        } else if (speaker === 'U') {
          htmlContent += `
            <div class="utterance_container_U">
              <div class="utterance_bubble background_U">
                <div class="utterance">${message}</div>
              </div>
            </div>`;
        }
      }
    }

    htmlContent += `</div></body></html>`;

    const outputHtmlPath = path.join(__dirname, 'temp.html');
    fs.writeFileSync(outputHtmlPath, htmlContent);

    await page.goto('file://' + outputHtmlPath);

    const screenshotPath = path.join(__dirname, path.join('dialogs', `${path.basename(file, '.txt')}.png`));
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });

    console.log(`Screenshot saved for ${file} as ${screenshotPath}`);

    exec(`convert "${screenshotPath}" -trim "${screenshotPath}"`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error during trimming: ${error.message}`);
        return;
      }
      if (stderr) {
        console.error(`stderr: ${stderr}`);
        return;
      }
      console.log(`Image trimmed and saved as ${screenshotPath}`);
    });

    fs.unlinkSync(outputHtmlPath);
  }

  await browser.close();
})();
