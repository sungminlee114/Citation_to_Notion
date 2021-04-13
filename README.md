**Citation_to_Notion**

This is a repository that contains some python3 files, which parse data out of references/citations that follow formats generally used at CS(embedded, mobile, system) domains using Google Scholar, and dictates it at a notion collection.

**Follow the prerequirements bellow before running.**
- Create a notion table which has columns named ['Name', 'Authors', 'Citation', 'Conference_Journal', 'Year', 'Link]. You may create more other columns if you want.
- From your browser inspecter, while viewing any page of your notion repository, copy the value of your cookie named 'token_v2' and paste it at variable 'NOTION_TOKEN_V2' inside the python code.
- Copy the url of your notion table and paste it at variable 'NOTION_COLLECTION_URL'
- From your browser inspecter, while viewing an arbitary search result page of Google Scholar, copy the value of your cookie string and paste it at variable 'GOOGLE_COOKIE' inside the python code. Do not close the browser or surfing into another page(i.e keep the page opened).

**After excuting the python code**
- Copy lines of references/citation texts and paste it at the console.
- Bellow the last line of your texts, enter qqq to indicate the end of input.

**Trouble shooting**
- While querying via google scholar, a captcha might appear (which we can't handle it via normal console application). Which you can get informed by an error message, "Connection Failed..". In this case, refresh the browser staying at google scholar. If a captha appears at your browser, solve it. If not, its okay. After that, copy and paste the new GOOGLE_COOKIE value into the python code and run it again.

This repository is currently made just for me and some of my aquaintances. Thus might not be neatly wrapped up for general users. Please ring the issue bell to let me know.

