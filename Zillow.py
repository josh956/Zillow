import requests
import pandas as pd
from datetime import datetime

url = "https://zillow-com1.p.rapidapi.com/valueHistory/localRentalRates"

querystring = {"address": "7 henchman street, boston MA 02114"}

headers = {
    "x-rapidapi-key": "b4d2e9c6d5msh991837d54243565p1fb678jsn2e0e96d5f959",
    "x-rapidapi-host": "zillow-com1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    
    # Extract 'chartData' and process the points
    if 'chartData' in data:
        points_list = []
        for chart in data['chartData']:
            if 'points' in chart:
                points_list.extend(chart['points'])
        
        # Convert to DataFrame
        df = pd.DataFrame(points_list)
        
        # Convert 'x' (timestamp) to datetime and extract year
        if 'x' in df.columns:
            df['Date'] = pd.to_datetime(df['x'], unit='ms')
            df['Year'] = df['Date'].dt.year
        
        # Rename columns for clarity
        df.rename(columns={'y': 'Value'}, inplace=True)
        
        # Group by year and calculate the average value
        yearly_avg = df.groupby('Year')['Value'].mean().reset_index()
        yearly_avg.rename(columns={'Value': 'Average_Rent'}, inplace=True)
        
        # Display the DataFrame
        print(yearly_avg)
    else:
        print("No 'chartData' found in the response.")
else:
    print(f"API request failed with status code {response.status_code}: {response.text}")
