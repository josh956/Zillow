import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit App
st.title("Zillow Rental Data Viewer")
st.write("Enter an address to fetch rental data and view yearly averages.")

# User input for the address
address = st.text_input("Address", value="7 Henchman Street, Boston, MA 02114")

if st.button("Fetch Data"):
    # API Details
    url = "https://zillow-com1.p.rapidapi.com/valueHistory/localRentalRates"
    headers = {
        "x-rapidapi-key": "b4d2e9c6d5msh991837d54243565p1fb678jsn2e0e96d5f959",
        "x-rapidapi-host": "zillow-com1.p.rapidapi.com"
    }
    querystring = {"address": address}

    try:
        # Fetch API Data
        response = requests.get(url, headers=headers, params=querystring)

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
                df['Date'] = pd.to_datetime(df['x'], unit='ms')
                df['Year'] = df['Date'].dt.year

                # Rename columns for clarity
                df.rename(columns={'y': 'Value'}, inplace=True)

                # Group by year and calculate the average value
                yearly_avg = df.groupby('Year')['Value'].mean().reset_index()
                yearly_avg.rename(columns={'Value': 'Average_Rent'}, inplace=True)

                # Calculate the percent change from the previous year
                yearly_avg['Percent_Change'] = yearly_avg['Average_Rent'].pct_change() * 100

                # Round the numbers and format percent change with '%'
                yearly_avg['Average_Rent'] = yearly_avg['Average_Rent'].round(0).astype(int)
                yearly_avg['Percent_Change'] = yearly_avg['Percent_Change'].round(0).fillna(0).astype(int).astype(str) + '%'

                # Ensure 'Year' is displayed as a string to prevent formatting with commas
                yearly_avg['Year'] = yearly_avg['Year'].astype(str)

                # Display the data
                st.write("Yearly Average Rent and Percent Change:")
                st.dataframe(yearly_avg)

                # Create a bar chart
                fig, ax = plt.subplots()
                ax.bar(yearly_avg['Year'], yearly_avg['Average_Rent'])
                ax.set_title("Yearly Average Rent")
                ax.set_xlabel("Year")
                ax.set_ylabel("Average Rent ($)")
                ax.set_ylim(1000, yearly_avg['Average_Rent'].max() * 1.1)  # Start y-axis at $1,000
                st.pyplot(fig)

            else:
                st.error("No rental data found for the given address.")

        elif response.status_code == 429:
            st.error("API request limit reached. Please try again later or check your API credit balance.")

        else:
            try:
                error_message = response.json().get('message', 'Unknown error occurred.')
            except Exception:
                error_message = "Unknown error occurred."
            st.error(f"API request failed with status code {response.status_code}: {error_message}")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while making the API request: {e}")
