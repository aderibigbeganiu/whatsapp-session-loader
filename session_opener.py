import asyncio
from playwright.async_api import async_playwright
# from playwright.sync_api import sync_playwright
import time
import environ

env = environ.Env()

env.read_env(".env")

INJECT_SESSION = '''
    async (data) => {
        const {SESSION_STRING, LOCAL_STRING} = data

        function getResultFromRequest(request) {
            return new Promise((resolve, reject) => {
                request.onsuccess = function(event) {
                    resolve(request.result);
                };
            })
        }

        async function getDB() {
            var request = window.indexedDB.open("wawc");
            return await getResultFromRequest(request);
        }

        async function injectSession(SESSION_STRING) {
            var db = await getDB();
            var objectStore = db.transaction("user", "readwrite").objectStore("user");

            for(var keyValue of session) {
                var request = objectStore.put(keyValue);
                await getResultFromRequest(request);
                localStorage.setItem(keyValue.key, keyValue.value)
            }
        }

        localStorage.clear()
        var local = JSON.parse(LOCAL_STRING);

        for(var i = 0; i < local.length; i++) {
            localStorage.setItem(local[i].key, local[i].value)
            console.log(local[i])
        }

        var session = JSON.parse(SESSION_STRING);
        await injectSession(session);
    }
'''


async def sessionGenerator(sessionFilePath, localFilePath):
    async with async_playwright() as p:
        # 2.1 Verify that session file is exist
        if sessionFilePath == "":
            raise IOError('"' + sessionFilePath + '" is not exist.')

        # 2.2 Read the given file into "session" variable
        with open(sessionFilePath, "r", encoding="utf-8") as sessionFile:
            session = sessionFile.read()

        with open(localFilePath, "r", encoding="utf-8") as localFile:
            local = localFile.read()

        # 2.3 Open Chrome browser
        browser = await p.chromium.launch(headless=False, devtools=True)
        context = await browser.new_context()

        # create a new page in a pristine context.
        page = await context.new_page()

        # 2.4 Open Web Whatsapp
        await page.goto("https://web.whatsapp.com")

        # 2.5 Wait for Web Whatsapp to be loaded properly
        await page.wait_for_selector("canvas")

        # 2.6 Execute javascript in browser to inject
        # session by using variable "session"
        print("Injecting session...")
        session = await page.evaluate(INJECT_SESSION, {"SESSION_STRING": session, "LOCAL_STRING": local})
        # time.sleep(60)

        await page.reload()
        time.sleep(600)


asyncio.run(sessionGenerator("session.wa", "local.wa"))
