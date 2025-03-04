# import requests
# import json

# # Define Jefferies' CIK
# cik = "0000096223"
# url = f"https://data.sec.gov/submissions/CIK{cik}.json"

# # Set up the User-Agent header (Replace with your real details)
# headers = {
#     "User-Agent": "LindaDominguez/linda.dominguez@widenet.ai"  # Change this to your real name/email
# }

# # Fetch data from SEC API
# response = requests.get(url, headers=headers)

# # Check response
# if response.status_code == 200:
#     data = response.json()
    
#     # Save the JSON data locally
#     with open("jefferies_filings.json", "w") as file:
#         json.dump(data, file, indent=4)

#     print("Data saved successfully!")
# else:
#     print(f"Error: {response.status_code}")
