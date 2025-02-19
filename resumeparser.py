# import libraries
import re
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
from googleapiclient.discovery import build
import google.generativeai as genai
from openai import OpenAI
import yaml
import altair as alt
import base64
import os

api_key = "AIzaSyBoycjQyZbAQJIfguvp695uFpZLD5AJMTM"
CONFIG_PATH = r"config.yaml"

# with open(CONFIG_PATH) as file:
#     data = yaml.load(file, Loader=yaml.FullLoader)
#     api_key = data['OPENAI_API_KEY']

def ats_extractor(resume_data, job_role):



    all_texts= []
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = '''
        You are an AI bot designed to act as a professional for parsing resumes. You are given with resume and your job is to extract the following information from the resume:
        1. full name
        2. email id
        3. github portfolio
        4. linkedin id
        5. employment details
        6. technical skills
        7. soft skills
        Give the extracted information in normal text format line by line in an organized manner!
        '''
    response = model.generate_content(f"{prompt} 'Here is the resume Details {resume_data}'")

    parsed_text = response.text
    parsed_text.replace("*", "")
    parsed_text = parsed_text.lstrip()
    all_texts.append(parsed_text)

    prompt = (f''
              f'I also want the ATS Score to be generated for the following resume for the job role {job_role} JUST GENERATE ME ONLY ATS SCORE OUT OF 100 LIKE ONLY I WANT THE INTEGRAL VALUE AS RESPONSE!\n')
    response = model.generate_content(f"{prompt} 'Here is the resume Details {resume_data}'")
    ats_text = response.text
    ats_text.replace("*", "")
    ats_text.replace("**", "")
    ats_text = ats_text.lstrip()
    all_texts.append(ats_text)

    prompt = (f''
              f'What are the missing keywords for my resume of job role {job_role}, generate me only 10 keywords one after another with bullets as numbers like 1) MATLAB 2) like that i want the bullets. dont generate any star symbols before the text give the bullets like 1. 2. like that')
    response = model.generate_content(f"{prompt} 'Here is the resume Details {resume_data}'")
    missing_keywords_text = response.text
    missing_keywords_text.replace("*", "")
    missing_keywords_text.replace("**", "")
    missing_keywords_text = missing_keywords_text.lstrip()
    all_texts.append(missing_keywords_text)

    prompt = (f''
              f'What are the gramatical errors in the resume? State in Point wise with bullets just generate me only points no extra heading or conclusion should be there for it just the text in points thats it! dont generate any star symbols before the text, just state every point in numbers just give me short points dont give big big points. Just give 5 mistakes thats it')
    response = model.generate_content(f"{prompt} 'Here is the resume Details {resume_data}'")
    errors_text = response.text
    errors_text.replace("*", "")
    errors_text.replace("**", "")
    errors_text = errors_text.lstrip()
    all_texts.append(errors_text)

    prompt = (f''
              f'What are the suggestions you would give for the betterment of this following resume irrespective of the job role in 5 points only! generate with bullet symbols, just after headings give : this symbol, just give me short points dont give big big points')
    response = model.generate_content(f"{prompt} 'Here is the resume Details {resume_data}'")
    suggestions_text = response.text
    suggestions_text.replace("*", "")
    suggestions_text.replace("**", "")
    suggestions_text = suggestions_text.lstrip()
    all_texts.append(suggestions_text)


    prompt = (f''
              f'What are the Current Trending news on the job role : {job_role} Generate only 3 sentences with a bullet for each point, just after headings give : this symbol just give me short points dont give big big points')
    response = model.generate_content(f"{prompt}")
    news_text = response.text
    news_text.replace("*", "")
    news_text.replace("**", "")
    news_text = news_text.lstrip()
    all_texts.append(news_text)

    prompt = (f''
              f'can you generate me some data of the job role {job_role} in the form of csv which should contain the column names as "year" and the "growth_rate" names should be of lower case only so that i can use it to plot a graph using matplotib'
              f'Just generate the text in .csv format not .csv file nothing more or less text just the data thats it no extra text!')
    response = model.generate_content(f"{prompt}")

    data = response.text
    clean_data = data.strip("```csv").strip("```").strip()
    clean_data=re.sub(r"\*\*", "", clean_data)

    df = pd.read_csv(StringIO(clean_data))

    plt.figure(figsize=(10, 6))
    plt.plot(df['year'], df['growth_rate'], marker='o', linestyle='-', color='blue')
    plt.title(f'Growth Rate of {job_role} Jobs Over Time')
    plt.xlabel('Year')
    plt.ylabel('Growth Rate (%)')
    plt.grid(True)

    output_dir = os.path.join("static", "images")
    jpeg_file = os.path.join(output_dir, "plot.jpg")

    plt.savefig(jpeg_file, format='jpeg', dpi=100)
    plt.close()
    all_texts.append(jpeg_file)

    return all_texts