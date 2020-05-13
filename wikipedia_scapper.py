from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import csv
import re
import unicodedata
import pandas as pd


url = 'https://en.wikipedia.org/wiki/COVID-19_pandemic_in_the_Republic_of_Ireland'
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
soup = BeautifulSoup(webpage,features="lxml")


table = soup.find( "table", {"class":"wikitable mw-collapsible"} )

# Unable extrct table header from code, explicitly using them as per the order in the website
header = ['Date', 'Carlow', 'Cavan', 'Clare', 'Cork', 'Donegal', 'Dublin', 'Galway', 'Kerry', 'Kildare', 'Kilkenny', 'Laois', 'Leitrim', 'Limerick', 'Longford', 'Louth', 'Mayo', 'Meath', 'Monaghan', 'Offaly', 'Roscommon', 'Sligo', 'Tipperary', 'Waterford', 'Westmeath', 'Wexford', 'Wicklow', 'New', 'Total']

total = []

# Writing the data ---> Saving total separately 
with open('IRE_Countywise_incidence_May12.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    for table_row in table.findAll('tr')[3:]:
        columns = table_row.findAll('td')
        h = table_row.findAll('th')
        output_row = []
        if h == []:
            
            for column in columns:
                if len(columns) > 2:
                    val = "".join(column.text.replace('N/A','0').split())
                    if val == '-': # Some values are '-' instead of NA, so imputing them to 0
                        val = 0
                    output_row.append(val)
            writer.writerow(output_row)
        else:
            for column in h:
                output_row.append("".join(column.text.replace('N/A','0').split()))
            total.append(output_row)

df = pd.read_csv('IRE_Countywise_incidence_May12.csv', encoding = "ISO-8859-1", engine='python')

# Converting data type 
for col in df.columns[1:]:
    df[col] = df[col].astype('int')

df.to_csv('IRE_Countywise_incidence_May12.csv')

