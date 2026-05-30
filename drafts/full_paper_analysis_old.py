import pandas as pd
import json

# The name of the text file you are pasting your results into
JSON_FILE_PATH = 'data/notebook_LM_analysis.txt'

# The unique separator you are typing between each JSON object
DELIMITER = '---END---'

def load_data_from_multiline_file(file_path):
    """
    Reads a single text file containing multiple JSON objects
    separated by a custom delimiter.
    """
    data_list = []
    
    print(f"Attempting to read data from '{file_path}'...")
    
    try:
        # 1. Read the ENTIRE file content into one big string
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

        # 2. Split the entire text into "blocks" using the delimiter
        json_blocks = full_text.split(DELIMITER)
        
        print(f"File read. Found {len(json_blocks)} potential JSON blocks.")

        # 3. Loop through each block, clean it, and parse it
        for i, block in enumerate(json_blocks):
            # Clean up any extra newlines or spaces around the JSON
            json_string = block.strip()
            
            # Skip any empty blocks (e.g., from the end of the file)
            if not json_string:
                continue
                
            try:
                # 4. Parse the (now clean) multi-line JSON string
                data = json.loads(json_string)
                data_list.append(data)
            except json.JSONDecodeError:
                print(f"---")
                print(f"Warning: Skipping malformed JSON block {i+1}.")
                print(f"This block did not contain valid JSON.")
                print(f"Block content (first 70 chars): {json_string[:70]}...")
                print(f"---")

        if not data_list:
            print("Error: No valid data was loaded. The file might be empty or unreadable.")
            return None

        # 5. Normalize the list of dictionaries into a DataFrame
        df = pd.json_normalize(data_list)
        return df, data_list

    except FileNotFoundError:
        print(f"---")
        print(f"CRITICAL ERROR: The file '{file_path}' was not found.")
        print("Please make sure your file is in the same directory as this script,")
        print("and that the name matches exactly.")
        print(f"---")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# --- Main part of the script ---
if __name__ == "__main__":
    
    df_papers, data_list = load_data_from_multiline_file(JSON_FILE_PATH)
    
    if df_papers is not None:
        print("\n--- Success! Data loaded into DataFrame. ---")
        



