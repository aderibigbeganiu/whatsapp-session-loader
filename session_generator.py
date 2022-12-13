import asyncio
from playwright.async_api import async_playwright
import time
import environ

env = environ.Env()

env.read_env(".env")

EXTRACT_SESSION = '''
    async () => {
        function getResultFromRequest(request) {
            return new Promise((resolve, reject) => {
                request.onsuccess = function (event) {
                    resolve(request.result);
                };
            });
        }

        async function getDB() {
            var request = window.indexedDB.open("wawc");
            return await getResultFromRequest(request);
        }

        async function readAllKeyValuePairs() {
            var db = await getDB();
            var objectStore = db.transaction("user").objectStore("user");
            var request = objectStore.getAll();
            return await getResultFromRequest(request);
        }
        session = await readAllKeyValuePairs();
        let local = [];
        for (const key in localStorage) {
            local.push({"key": `${key}`, "value": `${localStorage.getItem(key)}`})
        }
        return [JSON.stringify(session), JSON.stringify(local)];
    }
'''


async def sessionGenerator(sessionFilePath, localFilePath):
    # page.goto(f"https://web.whatsapp.com/send?phone={971000000000}")
    async with async_playwright() as p:
        # 1.1 Open Chrome browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # create a new page in a pristine context.
        page = await context.new_page()

        # 1.2 Open Web Whatsapp
        await page.goto("https://web.whatsapp.com")

        # 1.3 Ask user to scan QR code
        print("Waiting for QR code scan...")

        # 1.4 Wait for QR code to be scanned
        # page.wait_for_load_state('domcontentloaded')
        await page.wait_for_selector("#side")

        # 1.5 Execute javascript in browser and
        # extract the session text
        session, local = await page.evaluate(EXTRACT_SESSION)

        # 1.6 Save file with session text file with
        # custom file extension ".wa"
        with open(sessionFilePath, "w", encoding="utf-8") as sessionFile:
            sessionFile.write(str(session))
            print("Your session file is saved to: " + sessionFilePath)
        with open(localFilePath, "w", encoding="utf-8") as localFile:
            localFile.write(str(local))
            print("Your session file is saved to: " + localFilePath)


asyncio.run(sessionGenerator("session.wa", "local.wa"))
