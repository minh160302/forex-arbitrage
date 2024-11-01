const puppeteer = require('puppeteer');
const fs = require("fs");

(async () => {
  // Launch the browser
  const browser = await puppeteer.launch({
    // executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    // headless: false,
    // args: ["--window-size=2400,1239"]
  });
  const page = await browser.newPage();

  // Navigate to the desired page
  let pageIndex = 1
  console.log("START scraping");

  let csvData = [];

  while (true) {
    try {
      await page.goto(`https://www.centralcharts.com/en/price-list-ranking/ALL/asc/ts_48-forex-128-currency-pairs--qc_1-alphabetical-order?p=${pageIndex}`); // Replace with your actual page URL

      // Wait for the table to load (adjust selector as needed)
      await page.waitForSelector('table', { timeout: 5000 });
      // Extract table data
      const tableData = await page.evaluate(() => {
        const rows = Array.from(document.querySelectorAll('table tr')); // Select all rows
        return rows.map(row => {
          const cells = Array.from(row.querySelectorAll('th, td')); // Select all header or data cells
          return cells.slice(0, 9).map(cell => cell.textContent.trim()); // Extract and limit to 9 columns
        });
      });


      // Convert to CSV format
      const currentPageData = pageIndex == 1
        ? tableData.map(row => row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',')).join('\n')
        : tableData.splice(1).map(row => row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',')).join('\n');

      csvData.push(currentPageData);

      console.log(`Data page ${pageIndex} has been saved to current_price.csv`);
      pageIndex += 1;
    } catch (error) {
      console.log("END scraping");
      break;
    }

    // Write the CSV data to a file
    fs.writeFileSync('./dataset/current_price.csv', csvData.join("\n"), 'utf8');
  }
  // Close the browser
  await browser.close();
})();