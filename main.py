#!/usr/bin/env python3
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json, os, requests, heapq

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six

firebase_secret = os.environ['FB_SECRET']

# returns all the database entries as json
def get_Mastersheet():
    r = requests.get('https://imposter-hacks.firebaseio.com/ masterSheet.json?print=pretty&auth=' + firebase_secret).json()
    r.pop(0)
    return r

entries = get_Mastersheet()
num_of_entries = len(entries)

# finds sentiment of given text
def get_sentiment(text):
    """Detects sentiment in the text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects sentiment in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    sentiment = client.analyze_sentiment(document).document_sentiment

    return sentiment.score * sentiment.magnitude
   
# finds sentiment of specific company
def company_sentiment(company):
    sentiment = 0
    num_of_hits = 0
    for entry in entries:
        if entry[3] == company:
            num_of_hits += 1
            sentiment += get_sentiment(entry[10])
            sentiment += get_sentiment(entry[9])

    return sentiment / num_of_hits

# average salary based on gender and position
def average_salary_gender(gender, position):
    avg_salary = 0
    num_of_hits = 0
    for entry in entries:
        if entry[1] == gender and (entry[6] == position or position == 'any'):
            if entry[8] != 'n/a':
                num_of_hits += 1
                avg_salary += entry[8]

    if num_of_hits == 0:
        return 0 
    return avg_salary / num_of_hits

# returns top ten highest sentiment scoring companies
def top_ten():
    top10=[]
    visited=['n/a']
    for entry in entries:
        if entry[3] not in visited:
            visited.append(entry[3])
            heapq.heappush(top10, (company_sentiment(entry[3]), entry[3]))
    top10 = heapq.nlargest(10, (heapq.heappop(top10) for i in range(len(top10))))
    return top10

def main():
    topten = top_ten()
    topten = [i[1] for i in topten]
    average_male_intern = str(average_salary_gender('Male', 'Intern/co-op'))
    average_female_intern = str(average_salary_gender('Female', 'Intern/co-op'))
    average_male_fulltime = str(average_salary_gender('Male', 'Full-time'))
    average_female_fulltime = str(average_salary_gender('Female', 'Full-time'))
    print("Top Ten Companies" + topten)
    print("Average male intern salary: " + average_male_intern)
    print("Average female intern salary: " + average_female_intern)
    print("Average male full-time salary: " + average_male_fulltime)
    print("Average female full-time salary: " + average_female_fulltime)
    #index = render_template('public/index.html', topten1=topten[0], 
    #                                     topten2=topten[1], 
    #                                     topten3=topten[2],
    #                                     topten4=topten[3],
    #                                     topten5=topten[4],
    #                                     topten6=topten[5],
    #                                     topten7=topten[6],
    #                                     topten8=topten[7],
    #                                     topten9=topten[8],
    #                                     topten10=topten[9])
    
if __name__ == "__main__":
    main()
