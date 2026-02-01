"""
Test: Fetch data dari 1965 dengan indikator GDP baru
"""

import sys
sys.path.append('.')

from services.update_data_api import fetch_data_from_api

print("=" * 80)
print("TEST: Fetch Data dari 1965-1975 dengan GDP Constant 2015 US$")
print("=" * 80)
print()

result = fetch_data_from_api(data_type='all', start_year=1965, end_year=1975)

print("RESULT:")
print("-" * 80)
print(f"Success: {result.get('success')}")
print(f"Message: {result.get('message')}")
print(f"Energy Count: {result.get('energyCount')}")
print(f"GDP Count: {result.get('gdpCount')}")
print()

if result.get('alignment_info'):
    print("ALIGNMENT INFO:")
    print(f"  Common years: {result['alignment_info']['common_years']}")
    print(f"  Total matched: {result['alignment_info']['total_matched']}")
    print(f"  Year range: {result['alignment_info']['year_range']}")
    print(f"  Coverage: {result['alignment_info']['coverage_percentage']:.1f}%")
print()

# Check actual data files
import pandas as pd
import os

if os.path.exists('data/raw/energy.csv') and os.path.exists('data/raw/gdp.csv'):
    print("=" * 80)
    print("VERIFIKASI DATA TERSIMPAN:")
    print("=" * 80)
    print()
    
    energy = pd.read_csv('data/raw/energy.csv')
    gdp = pd.read_csv('data/raw/gdp.csv')
    
    print(f"Energy records: {len(energy)}")
    print(f"Energy years: {energy['Year'].min()}-{energy['Year'].max()}")
    print()
    print("Energy sample (first 5):")
    print(energy.head()[['Year', 'fossil_fuels__twh']])
    print()
    
    print(f"GDP records: {len(gdp)}")
    print(f"GDP years: {gdp['year'].min()}-{gdp['year'].max()}")
    print()
    print("GDP sample (first 5):")
    print(gdp.head())
    print()
    
    # Check 1965-1966 specifically
    energy_1965_66 = energy[energy['Year'].isin([1965, 1966])]
    gdp_1965_66 = gdp[gdp['year'].isin([1965, 1966])]
    
    print("=" * 80)
    print("DATA 1965-1966:")
    print("=" * 80)
    print()
    print("Energy 1965-1966:")
    if len(energy_1965_66) > 0:
        print(energy_1965_66[['Year', 'fossil_fuels__twh']])
    else:
        print("  ❌ TIDAK ADA")
    print()
    
    print("GDP 1965-1966:")
    if len(gdp_1965_66) > 0:
        print(gdp_1965_66)
        print()
        print("✅ BERHASIL! Data GDP 1965-1966 tersedia!")
    else:
        print("  ❌ TIDAK ADA")
    print()
