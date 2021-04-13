import enum
from notion.client import NotionClient
import requests
from bs4 import BeautifulSoup
import re
from difflib import SequenceMatcher
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'

UrlConvert = {
    '&' : "%26",
    '/' : "%2F",
    ':' : "%3A",
    '?' : "%3F",
    '=' : "%3D",
    ' ' : "+"
}
    	
NOTION_TOKEN_V2 = "<notion_v2_key>"
NOTION_COLLECTION_URL = "<notion_v2_url>"
GOOGLE_COOKIE = "<google_scholar_cookie>"

client = NotionClient(token_v2=NOTION_TOKEN_V2)
cv = client.get_collection_view(NOTION_COLLECTION_URL).collection

print("Reference string?(End : qqq):")
lines = []
while True:
    line = input()
    if line != "qqq":
        lines.append(line)
    else:
        break

ref_str = '\n'.join(lines).strip()
ref_str = ref_str.replace("\n", " ")

URL = "https://scholar.google.com/scholar?hl=ko&as_sdt=0%2C5&q="

summary_no_result = 0
summary_total_queried = 0

for query in ref_str.split("["):
    query = query[query.find("]")+1:]
    query = query.strip()
    
    #Get rid of urls
    query = re.sub(",?\s?h\\s?t\\s?t\\s?p\\s?s?\\s?:\\s?\/\\s?\/\\s?[-a-zA-Z0-9@:%._\+~#=\\s]{1,256}\.\s?[a-zA-Z0-9()\s]{1,6}\s?([-a-zA-Z0-9()@:%_\+.~#?&//=\s]*),?\s?", "", query)
    if query:
        summary_total_queried += 1
        print(f"---[{summary_total_queried} : {len(query)}]---")
        dot_1 = re.match("([A-Z]((.+?and (([A-Z]([A-Z]?|[a-z]{1,}(?= \d{4}|[A-Z]))[\.,]\s){1,3}))|(.+?et al\.)\s)|(.+?\.(?= \d{4})))", query)
        querys = []
        if dot_1 is not None:
            dot_1 = dot_1.end()
            part_1 = query[:dot_1 - 1].strip()
            querys = [part_1] + [q.strip() for q in re.split("\.(?!,)", query[dot_1:])]
        else:
            querys = [q.strip() for q in re.split("\.(?!,)", query)]
        
        querys = [q for q in querys if q != ""]
        print(querys)
        # continue

        query_str = ""
        l = 0
        for i, q in enumerate(querys):
            if i < len(querys) - 1:
                q+=". "
                
            l += len(q)
            if(l < 250):
                query_str += q
        
        query_strs = [query_str] + querys

        title_similar = 0
        result = None
        title_el = None

        for query_str in query_strs:
            if len(query_str) < 7:
                continue
                
            print(f"Querying [{query_str}]...\n")
            for k,v in UrlConvert.items():
                query_str = query_str.replace(k, v)
            queryURL = URL + query_str + "&btnG="

            response = requests.get(queryURL, headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36', 'cookie' : GOOGLE_COOKIE})
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find(id="gs_res_ccl_mid")

            if not response.ok or results is None:
                print(f"{bcolors.FAIL}Connection Failed.. {bcolors.WHITE}")
                if response.status_code == 429:
                    print(response.headers)
                    print(response.text)
                    exit()
                continue

            result_inner = results.find_all(class_ = "gs_ri")

            print(f"Total {len(result_inner)} results found.")

            for result in result_inner:
                title_el = result.find(class_="gs_rt").find("a")

                if title_el is None:
                    continue

                title = title_el.get_text()

                for q in querys:
                    if title is q:
                        title_similar = 1
                    else :
                        title_similar = max(SequenceMatcher(None, title.lower(), q.lower()).ratio(), title_similar)

                if title_similar > 0.5 and title_similar < 0.7:
                    print(title.lower(), ";", title_similar)

                if title_similar >= 0.7:
                    break

            if title_similar >= 0.7:
                print(f"Title similarity : {title_similar}, ()")
                break
        
        

        if title_similar < 0.7 or title_el is None or result is None:
            print(f"{bcolors.WARNING}No results..{bcolors.WHITE}")
            summary_no_result += 1
            continue

        
        
        # search_res = cv.get_rows(search=title)
        # if len(search_res) > 0 and search_res[0].name == title:
        #     summary_exsisting += 1
        #     print("Paper already is in table")
        #     continue

        link = title_el['href']
        
        author_str = result.find(class_ = "gs_a").get_text()
        author_str = author_str.replace("\xa0", " ").split(" - ")

        if len(author_str) == 3:
            authors, journal, _ = author_str
        elif len(author_str) == 2:
            authors, _ = author_str
        else:
            print(f"{bcolors.WARNING}Author info error. [{author_str}]{bcolors.WHITE}")
        
        year = re.findall('\d{4}', journal)
        if len(year) == 0:
            year = -1
        else:
            year = year[0]

        _journal = journal[:journal.rfind(year)].rstrip().lstrip().replace(",", "")

        if not _journal:
            journal = "Not specified"
        else:
            journal = _journal
        
        #from google
        # authors2 = authors.replace("…,", "").replace("…", "")
        # authors2 = authors2.replace(",", " ").replace("  ", " ").strip().lower()

        journal2 = journal.replace("…,", "").replace("…", "").rstrip().lstrip().lower()
        
        # flag_a = False
        flag_j = False
        for el in querys:
            _el = el
            el = el.lower()
            # print(authors2, ";", el.replace(",", " ").replace(".", " ").replace("  ", " "), SequenceMatcher(None, authors2, el.replace(",", " ").replace(".", " ").replace("  ", " ")).ratio())
            # if authors2 in el or SequenceMatcher(None, authors2, el.replace(",", " ").replace(".", " ").replace("  ", " ")).ratio() > 0.5:
            #     authors = _el
            #     flag_a = True
            #     continue
            
            # print(journal2, ";", el)
            if journal2 in el or SequenceMatcher(None, journal2, el).ratio() > 0.5:
                journal = _el
                flag_j = True
                continue
        
        # if not flag_a:
        #     print(f"{bcolors.OKBLUE}Authors not matched.[{authors2}]{bcolors.WHITE}")
        
        if not flag_j:
            print(f"{bcolors.OKBLUE}Journals not matched.[{journal2}]{bcolors.WHITE}")

        citation_str = result.find(class_="gs_fl")
        citation_num = re.findall('\d*회', citation_str.get_text())
        if len(citation_num) == 0:
            citation_num = 0
        else:
            citation_num = citation_num[0][:-1]

        print(f"title : {title}")
        print(f"link : {link}")
        print(f"authors : {authors}")
        print(f"journal : {journal}")
        print(f"year : {year}")
        print(f"citation : {citation_num}")
        print()

        year = int(year)
        citation_num = int(citation_num)
        
        # row = cv.add_row()
        # row.name = title
        # row.link = link
        # row.authors = authors
        # row.year = year
        # row.conference_journal = journal
        # row.citation = citation_num

        time.sleep(1)

print(f"{bcolors.OKGREEN}[Summary]\nOut of {summary_total_queried} querys,\nNo result : {summary_no_result}\n{bcolors.WHITE}")