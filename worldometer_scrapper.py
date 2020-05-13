from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import csv
import re
import unicodedata
import pandas as pd

url = 'https://www.worldometers.info/coronavirus/'
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
soup = BeautifulSoup(webpage,features="lxml")

# ---------------------------------------------------------------------------------PART 1--------------------------------------------------------


# Finding html table tag using class name
table = soup.find( "table", {"class":"table table-bordered table-hover main_table_countries"} )


#----------------------------------------------CSV header--------------------------------------------------

# Pattern get filter  table header
quoted = re.compile("(?<=')[^']+(?=')")
headers = [quoted.findall(unicodedata.normalize("NFKD",str(th.text.encode("utf8"))))[0] for th in table.select("tr th")]

# Even after urf 8 encoding got byte characters , manually replacing them [explicit]
replace_chars = ['\\n','\\','/',"xa0","xc2"]
csv_header = []
for i in headers:
    for char in replace_chars:
        i = i.replace(char,' ')
    csv_header.append(i.replace(' ','').split(',')[0])


#----------------------------------------------CSV Data--------------------------------------------------

with open('World_Tally_May_12.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(csv_header)
    for table_row in table.findAll('tr'):
        columns = table_row.findAll('td')
        output_row = []
        for column in columns:
            output_row.append("".join(column.text.replace(',','').replace('+','').split())) # repacing comma & + -->1,233 = 1233 & +23 = 23
        
        writer.writerow(output_row)

# Data Frame creation and saving csv

df = pd.read_csv('World_Tally_May_12.csv', encoding = "ISO-8859-1", engine='python')

# Filtering only countries as, countient tallies were extracted
df = df[df.Country != df.Continent]
df = df[~df.Country.isin(['Total:','World'])]

# Replacing NA with 0 as new cases are not confirmed yet
df.fillna(0,inplace = True)

# Converting datatype
for col in df.columns[1:-1]:
    df[col] = df[col].astype('int')

# Sort countries based on total cases
df = df.sort_values(by=['TotalCases'],ascending = False).reset_index(drop=True)

# Saving total data
df.to_csv('World_Tally_May_12.csv')

# Filtering only Ireland data
df[df.Country == 'Ireland'].to_csv('IRE_Latest_Figures_May12.csv')


# ---------------------------------------------------------------------------------PART 2--------------------------------------------------------

#--------------------------------------------------------------- Ireland -> Infected, recovered & dead daily record -----------------------------


url = 'https://www.worldometers.info/coronavirus/country/ireland/'

import requests
from bs4 import BeautifulSoup
import json
import codecs
from pandas.io.json import json_normalize

# Here data is read from HTML chart (javascript)
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Locate all the scripts tag
scripts = soup.find_all('script')

op_data_y_dic = {}

# Storing the graph names as in the html
graphs = ['graph-active-cases-total','coronavirus-cases-linear','coronavirus-deaths-linear']

# Reading the data
for script in scripts:
    for gph in graphs:
        if  gph in  script.text:
        
            # json parse and split lines
            encoded_string = script.text
            encoded_string  = encoded_string.split("JSON.parse('", 1)[-1].split('\n')
            for i,j in enumerate(encoded_string):
                if 'xAxis' in j: # extract xAxis values
                    s = encoded_string[i+1]
                    s = s[s.find("[")+1:s.find("]")]
                    s = [i.replace('"','').replace(' ','-')+'-2020' for i in s.split(',')]
                    index = s
                if 'data' in j: # Extract data ( y axis values)
                    s = encoded_string[i]
                    s = s[s.find("[")+1:s.find("]")]
                    s = [int(i) for i in s.split(',')]
                    op_data_y_dic[gph] = pd.Series(s)
                    

# Convert the dictonary to data frame
df = pd.DataFrame(op_data_y_dic)

# Index = data = Xaxis values---> Common for all the 3 graphs
df.index = index

# Calculating recovered from total cases and active & saving the csv
df.columns = ['total_cases','active','deaths']
df['Recovered'] = df['total_cases'] - df['active']
df.to_csv('IRE_Infected_Recoverd_Dead_Daywise_May12.csv')
