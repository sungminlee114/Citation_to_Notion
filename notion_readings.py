from notion.client import NotionClient
import requests
from bs4 import BeautifulSoup
import re

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

summary_exsisting = 0
summary_no_result = 0
summary_many_no_matching = 0
summary_total_queried = 0

for query in ref_str.split("["):
    query = query[query.find("]")+1:]
    if "http" in query and "//" in query:
        continue
    if query:
        summary_total_queried += 1
        print(f"---[{summary_total_queried} : {len(query)}]---")
        
        querys =[q.strip() for q in query.split(".")]
        query_str = ""
        l = 0
        for i, q in enumerate(querys):
            if i < len(querys) - 1:
                q+=". "
                
            l += len(q)
            if(l < 250):
                query_str += q
                
        print(f"Querying [{query_str}]...\n")
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
        else:
            if len(results) == 0:
                print(f"{bcolors.WARNING}No results..{bcolors.WHITE}")
                summary_no_result += 1
                continue

            result_inner = results.find_all(class_ = "gs_ri")

            manyFlag = True if len(result_inner) > 1 else False
            manyCnt = 0
            print(f"Total {len(result_inner)} results found.")

            # if manyFlag:
            #     print(f"{bcolors.WARNING}Total {len(result_inner)} results found. Check later.{bcolors.WHITE}")
            # else:
            #     print(f"Total {len(result_inner)} results found.")

            for result in result_inner:
                title_el = result.find(class_="gs_rt").find("a")
                title = title_el.get_text()

                if manyFlag:
                    if title not in querys:
                        continue
                    else:
                        manyCnt += 1

                search_res = cv.get_rows(search=title)
                if len(search_res) > 0 and search_res[0].name == title:
                    summary_exsisting += 1
                    print("Paper already is in table")
                    continue

                link = title_el['href']
                
                author_str = result.find(class_ = "gs_a").get_text()
                author_str = author_str.replace("\xa0", " ")

                authors, journal, _ = author_str.split(" - ")
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
                
                authors2 = authors.replace("…,", "").replace("…", "")
                authors2 = authors2[:authors2.find(",")].split(" ")
                authors2 = [auth for auth in authors2 if len(auth)>1][0]

                journal2 = journal.replace("…,", "").replace("…", "").rstrip().lstrip()
                
                flag_j = False
                flag_a = False
                for el in query.split("."):
                    if authors2 in el:
                        authors = el
                        flag_a = True
                        continue
                    if journal2 in el:
                        journal = el
                        flag_j = True
                        continue
                
                if not flag_a:
                    print(f"{bcolors.OKBLUE}Authors not matched.[{authors2}]{bcolors.WHITE}")
                
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
                
                row = cv.add_row()
                row.name = title
                row.link = link
                row.authors = authors
                row.year = year
                row.conference_journal = journal
                row.citation = citation_num

                if manyCnt > 0:
                    break
            
            if manyCnt == 0 and manyFlag:
                print(f"{bcolors.WARNING}Many results found, but none of the results matched.{bcolors.WHITE}")
                summary_many_no_matching += 1


print(f"{bcolors.OKGREEN}[Summary]\nOut of {summary_total_queried} of querys,\nExsisting : {summary_exsisting}\nNo result : {summary_no_result}\n Many but no matching result : {summary_many_no_matching}\n{bcolors.WHITE}")
