from bs4 import BeautifulSoup
import time
import requests
from random import randint
from html.parser import HTMLParser
import json
import math
import csv

DUCKDUCKGO_BASE_URL="https://duckduckgo.com/html/?q="
USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def simplify_url(url):
    url = url.lower()
    if url.startswith("http://"):
        url = url[7:]
    if url.startswith("www."):
        url = url[4:]
    if url.endswith("/"):
        url = url[:-1]
    return url

class SearchEngine:
    @staticmethod
    def search(query, sleep=True):
        if sleep: # Prevents loading too many pages too soon
            time.sleep(randint(10, 100))
            # time.sleep(randint(2, 5))
        temp_url = '+'.join(query.split()) #for adding + between words for the query
        url = DUCKDUCKGO_BASE_URL + temp_url
        # print(url)
        soup = BeautifulSoup(requests.get(url, headers=USER_AGENT).text, "html.parser")
        new_results = SearchEngine.scrape_search_result(soup)
        return new_results

    @staticmethod
    def scrape_search_result(soup):
        raw_results = soup.find_all('a',class_="result__a",href=True)
        results = []
        #implement a check to get only 10 results and also check that URLs must not be duplicated
        url_set=set()
        for result in raw_results:
            if len(results)==10:
                break
            link = result.get('href')
            duplicate=-1
            if 'ad_provider' in link.lower():
                print('ad_provider found')
                continue
            for appended_link in results:
                contender_link=simplify_url(link)
                appended_link=simplify_url(appended_link)
                if contender_link==appended_link:
                    duplicate=1
                    break

            if duplicate!=1:
                results.append(link)

        return results

#############Driver code############

# EXTRA
query_counter=0
# EXTRA

fp=open("queries","r")
all_queries=fp.readlines()

fp_j=open("hw1.json","w")

fp_gj=open("Google_Result4.json","r")

fp_csv=open("hw1.csv","w")

column_names=['Queries','Number of Overlapping Results','Percent Overlap','Spearman Coefficient']

writer_obj=csv.DictWriter(fp_csv,fieldnames=column_names)

writer_obj.writeheader()

output_dict={}



for query in all_queries:
    query_counter+=1
    output_dict[query.rstrip('\n')]=SearchEngine.search(query)
    print(query_counter)
    # if query_counter==5:
    #     break

query_counter=0

json.dump(output_dict,fp_j)

input_dict=json.load(fp_gj)

overlap_total=0
percent_total=0
spearman_coeff_total=0

query_number=0

for query in input_dict:
    query_number+=1
    google_list_raw=input_dict[query]
    duck_list_raw=output_dict[query]

    google_list=[]
    duck_list=[]
    for i in range(0,len(google_list_raw)):
        google_list.append(simplify_url(google_list_raw[i]))

    for i in range(0,len(duck_list_raw)):
        duck_list.append(simplify_url(duck_list_raw[i]))

    google_url_position_dict={}
    position=1
    for url in google_list:
        google_url_position_dict[simplify_url(url)]=position
        position+=1

    duck_url_position_dict = {}
    position = 1
    for url in duck_list:
        duck_url_position_dict[simplify_url(url)] = position
        position += 1

    number_overlap=0
    percent_overlap=0
    spearman_coeff=0

    for url in duck_list:
        if url in google_list:
            number_overlap+=1

    if number_overlap==0:
        spearman_coeff = 0

    elif number_overlap==1:
        spearman_coeff=0
        for url in duck_url_position_dict:
            if url in google_url_position_dict:
                if google_url_position_dict[url]==duck_url_position_dict[url]:
                    spearman_coeff=1
                    break
    else:
        summation_disq=0
        for url in duck_url_position_dict:
            if url in google_url_position_dict:
                summation_disq+=math.pow(duck_url_position_dict[url]-google_url_position_dict[url],2)

        spearman_coeff=1-( (6*summation_disq) /(number_overlap*(math.pow(number_overlap,2)-1)))

    percent_overlap=(number_overlap/10)*100

    # print(number_overlap,percent_overlap,spearman_coeff)

    writer_obj.writerow(({'Queries':'Query '+str(query_number), 'Number of Overlapping Results':number_overlap, 'Percent Overlap':percent_overlap, 'Spearman Coefficient':spearman_coeff}))
    overlap_total+=number_overlap
    percent_total+=percent_overlap
    spearman_coeff_total+=spearman_coeff

    query_counter+=1
    print(query_counter)

    # # EXTRA
    # query_counter+=1
    #
    # if(query_counter==5):
    #     break
    # # EXTRA


# number_of_queries=len(all_queries)
number_overlap_avg=overlap_total/query_counter
percent_overlap_avg=percent_total/query_counter
spearman_coeff_avg=spearman_coeff_total/query_counter

writer_obj.writerow(({'Queries': 'Averages', 'Number of Overlapping Results': number_overlap_avg,
                      'Percent Overlap': percent_overlap_avg, 'Spearman Coefficient': spearman_coeff_avg}))

fp.close()
fp_j.close()

#####################################