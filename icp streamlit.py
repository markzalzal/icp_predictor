#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import time
import re
import streamlit as st


# In[2]:


def is_valid_url(url):
    # Basic structure validation using regex
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    if regex.match(url):
        # Domain validation
        try:
            response = requests.get(url, timeout=5)
            return True
        except requests.RequestException:
            return False
    return False


def scrape_website(url, delay=0.1):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3"
    }
    
    try:
        time.sleep(delay)  # Introducing delay
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Use BeautifulSoup to parse the content and extract visible text
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):  # Remove script and style elements
            script.extract()
        return " ".join(soup.stripped_strings)  # Get visible text
    except requests.RequestException as e:
        print(f"Error scraping {url}. Error: {e}")
        return None


def determine_type(content):
    # Keywords for agency and SaaS
    agency = [
       "agency", "consultancy", "clients", "campaigns", "branding", "advertising", 
        "strategy", "creative", "design", "promotion", "media", "public relations", 
        "seo", "sem", "digital marketing", "content creation", "storytelling", 
        "insights", "production", "analytics", "collaboration", "storyboard", 
        "engagement", "outreach", "target audience", "graphic design", "user experience", 
        "video production", "multimedia", "campaign"
    ]
    saas = [
        "software", "platform", "dashboard", "subscription", "cloud", "integration", 
        "api", "automation", "scalability", "features", "solution", "updates", 
        "user management", "analytics", "reporting", "synchronization", "security", 
        "encryption", "onboarding", "customization", "workflow", "collaboration", 
        "deployment", "infrastructure", "support", "maintenance", "uptime", 
        "backup", "storage", "service level agreement", "subscriptions", "softwares", 
        "cloud-based", "integrate", "interface", "in one place", "all-in-one", "system", "pricing"
    ]
    
    agency_count = sum(content.count(word) for word in agency)
    saas_count = sum(content.count(word) for word in saas)

    if saas_count + agency_count ==0:
        return "No data found"
    elif saas_count + agency_count <3:
#        return [f"Not enough info, Agency:{round(agency_count/(agency_count + saas_count)*100,2)}%, SaaS:{round(saas_count/(agency_count + saas_count)*100,2)}%"]
        return ["Not enough info"]
    elif agency_count > saas_count:
        return [f'Agency: {round(agency_count/(agency_count + saas_count)*100,2)}%']
    elif saas_count > agency_count:
        return [f'Saas: {round(saas_count/(agency_count + saas_count)*100,2)}%']
    else:
        return ["Undetermined", agency_count, saas_count]


# In[3]:


def main():
    st.title('Website Type Analyzer')

    url = st.text_input('Enter the URL of the website:', '')

    if st.button('Analyze'):
        if url:
            if is_valid_url(url):
                content = scrape_website(url, delay=0.1)
                if content:
                    type_of_company = determine_type(content.lower())
                    st.success(f"The company is likely a(n): {type_of_company}")
                else:
                    st.error("Couldn't determine the type of company.")
            else:
                st.error("The provided URL is not valid.")
        else:
            st.error("Please enter a URL.")

if __name__ == "__main__":
    main()

