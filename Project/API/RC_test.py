import requests

userCountry = input("Enter a country:\n >")
baseUrl = "https://restcountries.com/v3.1/name/" + userCountry.lower()

response = requests.get(baseUrl, timeout=10)
print(f"Status code: {response.status_code}")

if response.ok:
    data = response.json()
    country = data[0]
    print(f"Country: {country["name"]["common"]}")
    print(f"Capital: {country.get("capital", ["unknown"])[0]}")
    print(f"Region : {country.get("region")}")
else:
    print(f"Error: {response.text}")
