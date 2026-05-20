import requests
import pandas as pd

import joblib

import re

def get_osf_metadata_comprehensive(filters):
    """
    Fetches OSF registrations using multiple filters and returns all attributes,
    including the unique Registry ID (GUID).
    """
    # Construct the base URL
    base_url = "https://api.osf.io/v2/registrations/"
    
    # Build filter string
   
    #url=f'{base_url}?&filter[description]=scoping review Large Language Model&page[size]=10000'
    filter_params = "&".join([f"filter[{k}]={v}" for k, v in filters.items()])
    url = f"{base_url}?{filter_params}&page[size]=10000"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        registrations = data['data']
        
        records = []
        for reg in registrations:
            # 1. Start with the unique GUID found at the top level
            record = {'id': reg['id']}
            
            # 2. Add the URL directly for easy access in your audit
            record['url'] = f"https://osf.io/{reg['id']}/"
            
            # 3. Update the dictionary with all items in the 'attributes' block
            record.update(reg['attributes'])
            
            records.append(record)
        
        return pd.DataFrame(records)
    else:
        print(f"Error {response.status_code}: {response.text}")
        return pd.DataFrame()

# Execution with your criteria
search_criteria = {
    "description": "Large Language Model"
}

df = get_osf_metadata_comprehensive(search_criteria)

df.shape

df['description'][0]

# Ensure the 'id' column is at the beginning for better visibility
if not df.empty:
    cols = ['id'] + [c for c in df.columns if c != 'id']
    df = df[cols]



df.to_excel("H:/Mi unidad/cod1/TUAI_review_scrapers/outputs/osf_registrations.xlsx", index=False)

df['subjects']



df



#################### general search ##########################
def get_osf_metadata_comprehensive(terms, fields):
    base_url = "https://api.osf.io/v2/registrations/"
    records = []
    seen_ids = set()

    for term in terms:
        filter_params = "&".join([f"filter[{f}]={term}" for f in fields])
        url = f"{base_url}?{filter_params}&page[size]=100"

        while url:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for reg in data['data']:
                    if reg['id'] not in seen_ids:  # avoid duplicates
                        seen_ids.add(reg['id'])
                        record = {'id': reg['id']}
                        record['url'] = f"https://osf.io/{reg['id']}/"
                        record.update(reg['attributes'])
                        records.append(record)
                url = data['links'].get('next')
            else:
                print(f"Error {response.status_code}: {response.text}")
                break

    return pd.DataFrame(records)


    # Usage
results = get_osf_metadata_comprehensive(
    terms=["Multimodal Large Language Model"],
    fields=["description"]
)

results.shape


joblib.dump(results, "H:/Mi unidad/cod1/TUAI_review_scrapers/outputs/multimodal_LLM_registrations.joblib")




df_fullword = joblib.load("H:/Mi unidad/cod1/TUAI_review_scrapers/outputs/large_registrations2.joblib")
df_fullword.shape


df_acronyms = joblib.load("H:/Mi unidad/cod1/TUAI_review_scrapers/outputs/llm_lmmosf_registrations.joblib")
df_acronyms.shape
df_acronyms.to_excel("H:/Mi unidad/cod1/TUAI_review_scrapers/outputs/llm_lmmosf_registrations.xlsx", index=False)

df_MLMM=joblib.load("H:/Mi unidad/cod1/TUAI_review_scrapers/outputs/multimodal_LLM_registrations.joblib")
df_MLMM.shape


df_concatenated = pd.concat([df_fullword, df_acronyms, df_MLMM])
df_concatenated.shape

df_concatenated['id'].nunique()

df_concatenated2 = df_concatenated.drop_duplicates(subset='id', keep='last')

df_concatenated2.to_excel("H:/Mi unidad/cod1/TUAI_review_scrapers/outputs/concatenated_registrations.xlsx", index=False)    


########### filter data #############


# ── PATTERNS ──────────────────────────────────────────────────────────────────

llm_pattern = re.compile(r"""
    \b(
        large \s+ language \s+ model s? |
        large \s+ multimodal \s+ model s? |
        multimodal \s+ language \s+ model s?
    )\b
""", re.IGNORECASE | re.VERBOSE)

clinical_pattern = re.compile(r"""
    \b(
        clinical |
        healthcare |
        health \s+ care |
        health |
        medicine |
        medical
    )\b
""", re.IGNORECASE | re.VERBOSE)

review_pattern = re.compile(r"""
    \b(
        scoping \s+ review |
        systematic \s+ review
    )\b
""", re.IGNORECASE | re.VERBOSE)

# ── FILTER ────────────────────────────────────────────────────────────────────

def matches_all(text):
    if not isinstance(text, str):
        return False
    return (
        bool(llm_pattern.search(text)) and
        bool(clinical_pattern.search(text)) and
        bool(review_pattern.search(text))
    )

df_filtered = df_concatenated[
    df_concatenated['description'].apply(matches_all) |
    df_concatenated['title'].apply(matches_all)
].reset_index(drop=True)

print(f"Total registries after filter: {len(df_filtered)}")
df_filtered[['id', 'title', 'url','description']].to_excel("H:/Mi unidad/cod1/TUAI_review_scrapers/outputs/filtered_osf_registrations.xlsx", index=False)