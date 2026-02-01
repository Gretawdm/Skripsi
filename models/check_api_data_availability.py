"""
Test: Cek data availability dari API untuk tahun 1965-1970

Script ini mengecek apakah data energi dan GDP benar-benar tersedia
mulai tahun 1965, dan jika tidak, tahun berapa data mulai tersedia.
"""

import pandas as pd
import requests

def check_data_availability():
    print("=" * 80)
    print("CEK KETERSEDIAAN DATA DARI API")
    print("=" * 80)
    print()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # ===== CHECK ENERGY DATA =====
    print("1. CHECKING ENERGY DATA (OWID)")
    print("-" * 80)
    
    energy_url = "https://ourworldindata.org/grapher/fossil-fuel-primary-energy.csv?v=1&csvType=full&useColumnShortNames=true"
    energy_df = pd.read_csv(energy_url, storage_options=headers)
    
    # Filter Indonesia
    energy_indonesia = energy_df[energy_df["Entity"] == "Indonesia"].copy()
    
    print(f"Total records untuk Indonesia: {len(energy_indonesia)}")
    print(f"Columns: {list(energy_indonesia.columns)}")
    print()
    
    if "Year" in energy_indonesia.columns:
        energy_indonesia = energy_indonesia.sort_values("Year")
        min_year = energy_indonesia["Year"].min()
        max_year = energy_indonesia["Year"].max()
        
        print(f"Tahun tersedia: {min_year} - {max_year}")
        print()
        
        # Check 1965-1975
        print("Data untuk tahun 1965-1975:")
        early_years = energy_indonesia[
            (energy_indonesia["Year"] >= 1965) & 
            (energy_indonesia["Year"] <= 1975)
        ]
        
        if len(early_years) > 0:
            print(early_years[["Year", "fossil_fuels__twh"]].to_string(index=False))
        else:
            print("  ❌ TIDAK ADA DATA untuk tahun 1965-1975")
            print(f"  ⚠️ Data mulai tersedia dari tahun: {min_year}")
        print()
        
        # Show first 10 records
        print("10 Record pertama:")
        print(energy_indonesia.head(10)[["Year", "fossil_fuels__twh"]].to_string(index=False))
    
    print()
    print()
    
    # ===== CHECK GDP DATA =====
    print("2. CHECKING GDP DATA (World Bank)")
    print("-" * 80)
    
    gdp_url = "https://api.worldbank.org/v2/country/IDN/indicator/NY.GDP.MKTP.CD?format=json&per_page=100"
    gdp_json = requests.get(gdp_url, headers=headers).json()
    
    if len(gdp_json) > 1:
        gdp_data = gdp_json[1]
        
        # Filter non-null values
        gdp_valid = [d for d in gdp_data if d["value"] is not None]
        
        print(f"Total records dengan nilai: {len(gdp_valid)}")
        
        years = sorted([int(d["date"]) for d in gdp_valid])
        min_year = min(years)
        max_year = max(years)
        
        print(f"Tahun tersedia: {min_year} - {max_year}")
        print()
        
        # Check 1965-1975
        print("Data untuk tahun 1965-1975:")
        early_gdp = [d for d in gdp_valid if 1965 <= int(d["date"]) <= 1975]
        
        if early_gdp:
            for d in sorted(early_gdp, key=lambda x: int(x["date"])):
                gdp_billion = d["value"] / 1_000_000_000
                print(f"  {d['date']}: ${gdp_billion:,.2f} Billion")
        else:
            print("  ❌ TIDAK ADA DATA untuk tahun 1965-1975")
            print(f"  ⚠️ Data mulai tersedia dari tahun: {min_year}")
        print()
        
        # Show first 10 records
        print("10 Record pertama (sorted by year):")
        first_10 = sorted(gdp_valid, key=lambda x: int(x["date"]))[:10]
        for d in first_10:
            gdp_billion = d["value"] / 1_000_000_000
            print(f"  {d['date']}: ${gdp_billion:,.2f} Billion")
    
    print()
    print()
    
    # ===== INTERSECTION CHECK =====
    print("3. CHECKING INTERSECTION (Common Years)")
    print("-" * 80)
    
    energy_years = set(energy_indonesia["Year"].unique())
    gdp_years = set([int(d["date"]) for d in gdp_valid])
    
    common_years = sorted(energy_years.intersection(gdp_years))
    
    print(f"Energy years count: {len(energy_years)}")
    print(f"GDP years count: {len(gdp_years)}")
    print(f"Common years count: {len(common_years)}")
    print()
    
    if common_years:
        print(f"Common years range: {min(common_years)} - {max(common_years)}")
        print()
        print("First 20 common years:")
        print(common_years[:20])
        print()
        
        # Check if 1965-1970 in common
        early_common = [y for y in common_years if 1965 <= y <= 1970]
        if early_common:
            print(f"✓ Tahun 1965-1970 tersedia: {early_common}")
        else:
            print(f"❌ Tahun 1965-1970 TIDAK tersedia dalam common years")
            print(f"⚠️ Common years mulai dari: {min(common_years)}")
    
    print()
    print("=" * 80)
    print("KESIMPULAN:")
    print("=" * 80)
    
    energy_min = int(energy_indonesia["Year"].min())
    gdp_min = min([int(d["date"]) for d in gdp_valid])
    common_min = min(common_years) if common_years else None
    
    print(f"Energy data mulai: {energy_min}")
    print(f"GDP data mulai: {gdp_min}")
    print(f"Common data (intersection) mulai: {common_min}")
    print()
    
    if common_min and common_min > 1965:
        print(f"⚠️ ALASAN: Meskipun ada data individual dari tahun lebih awal,")
        print(f"   data yang COCOK (matching) antara energi dan GDP baru mulai {common_min}")
        print()
        print("REKOMENDASI:")
        print(f"  → Gunakan tahun mulai: {common_min}")
        print(f"  → Atau cek apakah ada missing data di salah satu sumber")
    

if __name__ == "__main__":
    check_data_availability()
