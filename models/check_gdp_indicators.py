"""
Cek semua indikator GDP World Bank untuk Indonesia
Untuk menemukan indikator mana yang punya data paling lengkap (mulai dari tahun paling awal)
"""

import requests
import pandas as pd

def check_all_gdp_indicators():
    print("=" * 80)
    print("CEK SEMUA INDIKATOR GDP WORLD BANK UNTUK INDONESIA")
    print("=" * 80)
    print()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Daftar indikator GDP yang umum digunakan
    gdp_indicators = {
        'NY.GDP.MKTP.CD': 'GDP (current US$)',
        'NY.GDP.MKTP.KD': 'GDP (constant 2015 US$)',
        'NY.GDP.MKTP.CN': 'GDP (current LCU)',
        'NY.GDP.MKTP.KN': 'GDP (constant LCU)',
        'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
        'NY.GDP.PCAP.KD': 'GDP per capita (constant 2015 US$)',
    }
    
    results = []
    
    for indicator_code, indicator_name in gdp_indicators.items():
        print(f"Checking: {indicator_code} - {indicator_name}")
        print("-" * 80)
        
        try:
            url = f"https://api.worldbank.org/v2/country/IDN/indicator/{indicator_code}?format=json&per_page=100"
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if len(data) > 1:
                gdp_data = [d for d in data[1] if d["value"] is not None]
                
                if gdp_data:
                    years = sorted([int(d["date"]) for d in gdp_data])
                    min_year = min(years)
                    max_year = max(years)
                    count = len(years)
                    
                    print(f"  ✓ Data tersedia: {min_year} - {max_year} ({count} tahun)")
                    
                    # Show first 5 years
                    print(f"  Sample data (5 tahun pertama):")
                    for d in sorted(gdp_data, key=lambda x: int(x["date"]))[:5]:
                        value = d["value"]
                        if value > 1e12:  # Very large number
                            print(f"    {d['date']}: {value/1e12:.2f} Trillion")
                        elif value > 1e9:  # Billions
                            print(f"    {d['date']}: {value/1e9:.2f} Billion")
                        else:
                            print(f"    {d['date']}: {value:.2f}")
                    
                    results.append({
                        'Indicator': indicator_code,
                        'Name': indicator_name,
                        'Start Year': min_year,
                        'End Year': max_year,
                        'Total Years': count,
                        'Sample Value': gdp_data[0]['value']
                    })
                else:
                    print(f"  ✗ No data available")
                    results.append({
                        'Indicator': indicator_code,
                        'Name': indicator_name,
                        'Start Year': None,
                        'End Year': None,
                        'Total Years': 0,
                        'Sample Value': None
                    })
            else:
                print(f"  ✗ API error or no data")
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
        
        print()
    
    # Summary table
    print()
    print("=" * 80)
    print("SUMMARY: PERBANDINGAN INDIKATOR GDP")
    print("=" * 80)
    print()
    
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print()
    
    # Recommendation
    print("=" * 80)
    print("REKOMENDASI")
    print("=" * 80)
    print()
    
    # Find earliest start year
    valid_indicators = df[df['Start Year'].notna()].sort_values('Start Year')
    
    if not valid_indicators.empty:
        best = valid_indicators.iloc[0]
        print(f"🏆 INDIKATOR DENGAN DATA PALING LENGKAP:")
        print(f"   Code: {best['Indicator']}")
        print(f"   Name: {best['Name']}")
        print(f"   Period: {int(best['Start Year'])}-{int(best['End Year'])} ({int(best['Total Years'])} tahun)")
        print()
        
        # Current vs recommended
        current = df[df['Indicator'] == 'NY.GDP.MKTP.CD'].iloc[0]
        print(f"PERBANDINGAN:")
        print(f"  Current (NY.GDP.MKTP.CD):")
        print(f"    - Period: {int(current['Start Year']) if current['Start Year'] else 'N/A'}-{int(current['End Year']) if current['End Year'] else 'N/A'}")
        print(f"    - Total: {int(current['Total Years'])} tahun")
        print()
        print(f"  Recommended ({best['Indicator']}):")
        print(f"    - Period: {int(best['Start Year'])}-{int(best['End Year'])}")
        print(f"    - Total: {int(best['Total Years'])} tahun")
        print(f"    - Gain: +{int(best['Total Years']) - int(current['Total Years'])} tahun")
        print()
        
        print("CATATAN:")
        print("  - Constant US$ lebih baik untuk time series (adjusted for inflation)")
        print("  - Current US$ dipengaruhi inflasi dan nilai tukar")
        print("  - Untuk ARIMAX, disarankan gunakan constant price")
        print()
        
        return best['Indicator']
    
    return None


if __name__ == "__main__":
    recommended = check_all_gdp_indicators()
    
    if recommended:
        print()
        print("=" * 80)
        print(f"ACTION: Update sistem untuk menggunakan {recommended}")
        print("=" * 80)
