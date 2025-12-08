import requests

year = 2025
countryCode = input("Please enter Country Code\n > ")
baseUrl = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{countryCode}"

response = requests.get(baseUrl, timeout=10)
print(f"Status code: {response.status_code}")

if response.status_code == 204:
    print(f"No public holiday data returned for {countryCode} in {year}")
elif response.ok:
    holidays = response.json()
    print(f"Found {len(holidays)} holidays fpr {countryCode} in {year}.")
    for h in holidays[:5]:
        print(f"{h['date']} - {h['localName']}")
else:
    print(f"Error: {response.text}")
