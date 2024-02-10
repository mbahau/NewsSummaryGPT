#NewsGenerationGPT that will summarise the top news at day level.  Starting date will be 31st January 2024 to 2015
# Local setup ok


# Example: reuse your existing OpenAI setup
from openai import OpenAI
from googlesearch import search
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

for day in range(0,1):

  try:
    currentdate = pd.read_parquet('currentdate.parquet')
  except:
    currentdate = pd.DataFrame([pd.to_datetime("31-01-2024")], columns = ['Date'] )
    currentdate['DateM'] = currentdate['Date'].dt.strftime('%d %B %Y')


  query = str(currentdate['DateM'].values[0]) + " top news India"

 

  fetched_urls  = []
  result ="Below information is the google search of : " + query + ". From the below reults, give the recommendation which is(are) the best result(s) i got.\n"
  i=1
  for j in search(query, advanced=True, num_results= 5):
      # print(j)
      if "youtube" not in j.url:
          temp = str(i)+". *URL:"+j.url+" *Title: "+j.title+" *Description: "+j.description+".\n" 
          fetched_urls.append(j.url)
          result = result+temp
          i=i+1
  # result =  result+"\n\n"+" Analyse the above search results, and tell me which one is more related with the query searched . Answer in one word only, just give me the serial number so that i can refer it."
  result =  result+"\n\n"+"Analyse the above search results, and tell me 3 reference which is(are) the relevant result(s). Also give me the provided url(s) of the corresponding result(s). Note: Refer only the provided URLs with this text dont refer any other reference. Put the url inside double quotes"

  print(result)
  # ****
  # feeding the input for correct search to nodel 

  systemrole = "answer user query, the best you can serve user"

  completion = client.chat.completions.create(
    model="local-model", # this field is currently unused
    messages=[
      {"role": "system", "content": systemrole},
      {"role": "user", "content": result},
    ],
    temperature=0.7,
  )

  print(completion.choices[0].message.content)


  recommendation = completion.choices[0].message.content.split("<")
  recommendation

  recommendation = [ x for x in recommendation if "http" in x ]
  recommendation


  recommendation_final = []
  for item in recommendation:
      recommendation_final.append(item.split(">")[0])
      # print(item.split(">"))
  recommendation_final


  # recommendation_final[0]
  final_urls = [] 
  for rec_url in recommendation_final:
      for tu in fetched_urls:
          # print(tu)
          if rec_url in tu:
              # print(tu)
              final_urls.append(tu)


  i=0
  content  = ""
  ref_url = ""
  for urltmp in final_urls:
      
      # reference url 
      ref_url = ref_url + str(urltmp) + "\n"

      # Specify the URL of the website you want to scrape
      url = urltmp  # Replace with the actual URL

      # Send an HTTP GET request to the website
      response = requests.get(url)

      # Get the HTML content of the page
      html_content = response.text

      # Parse the HTML using BeautifulSoup
      soup = BeautifulSoup(html_content, "html.parser")
      # soup =  BeautifulSoup(s) #parse html with BeautifulSoup
      td = "Result "+ str(i)+". "+str(soup.text) +".\n"#tag of interest <td>Example information</td>
      content = content+td
      i=i+1
      if(i>2):
          break


  # systemrole = "answer user query very the best you can serve user"

  result = "Below is the News of  "+ query +". Summarise the different News in bullet points. Don't repeat duplicate news. Make it inseresting for user with the facts:\n"
  result =  result+str(" ".join(content.split()))
  result = result+"\n Summarise the News in bullet points."

  completion = client.chat.completions.create(
    model="local-model", # this field is currently unused
    messages=[
      # {"role": "system", "content": systemrole},
      {"role": "user", "content": result},
    ],
    temperature=0.7,
  )
  del result
  print(completion.choices[0].message.content)

  # saving the LLM model output
  data = "News of "+str(currentdate['DateM'].values[0])+'\n\n'
  data =  data + str(completion.choices[0].message.content)

  # need to provide the reference of the source news 
  data = data +"\n\n"
  data = data + "Reference:\n" + ref_url
  print("*** URLs:", ref_url)

  with open('Output/'+str(currentdate['Date'].values[0])[:10]+'.txt' , 'w') as f:
    f.write(data)
    del data

  currentdate['Date'] = currentdate['Date'] + pd.offsets.Day(-1)
  currentdate['DateM'] = currentdate['Date'].dt.strftime('%d %B %Y')
  currentdate.to_parquet('currentdate.parquet')