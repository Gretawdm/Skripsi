import pandas as pd
import requests
from flask import jsonify
from datetime import datetime
import os
from services.data_mysql_service import save_energy_to_db, save_gdp_to_db, init_data_tables
from services.database_service import save_data_update_history

def update_from_api():
    # Headers untuk menghindari 403 Forbidden
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # OWID Energy
    energy_url = "https://ourworldindata.org/grapher/fossil-fuel-primary-energy.csv?v=1&csvType=full&useColumnShortNames=true"
    energy_df = pd.read_csv(energy_url, storage_options=headers)

    # Filter Indonesia
    energy_df = energy_df[energy_df["Entity"] == "Indonesia"]

    # World Bank GDP
    gdp_url = "https://api.worldbank.org/v2/country/IDN/indicator/NY.GDP.MKTP.CD?format=json"
    gdp_json = requests.get(gdp_url, headers=headers).json()

    gdp_df = pd.DataFrame([
        {"year": int(d["date"]), "gdp": d["value"]}
        for d in gdp_json[1] if d["value"] is not None
    ])
    
    # Convert GDP to Billion USD untuk scale yang lebih comparable
    gdp_df["gdp"] = gdp_df["gdp"] / 1_000_000_000

    energy_df.to_csv("data/raw/energy.csv", index=False)
    gdp_df.to_csv("data/raw/gdp.csv", index=False)

    return {
        "energy_columns": list(energy_df.columns),
        "energy_rows": len(energy_df),
        "energy_sample": energy_df.head(5).to_dict(),

        "gdp_columns": list(gdp_df.columns),
        "gdp_rows": len(gdp_df),
        "gdp_sample": gdp_df.head(5).to_dict()
    }


def fetch_data_from_api(data_type='all', start_year=1990, end_year=2023):
    """
    Fetch data dari API dengan filter tahun dan tipe data
    
    Args:
        data_type: 'all', 'energy', atau 'gdp'
        start_year: tahun mulai
        end_year: tahun akhir
    """
    try:
        # Validasi input
        if start_year > end_year:
            return {
                "success": False,
                "message": f"Tahun mulai ({start_year}) tidak boleh lebih besar dari tahun akhir ({end_year})"
            }
        
        # Warning jika tahun mulai < 1960 (GDP constant 2015 US$ tersedia mulai 1960)
        if start_year < 1960 and data_type in ['all', 'gdp']:
            return {
                "success": False,
                "message": f"⚠️ Data GDP Indonesia (constant 2015 US$) dari World Bank tersedia mulai tahun 1960. Tahun mulai yang Anda minta ({start_year}) terlalu awal. Silakan gunakan tahun mulai minimal 1960.",
                "details": {
                    "energy_availability": "1965-sekarang (OWID)",
                    "gdp_availability": "1960-sekarang (World Bank - NY.GDP.MKTP.KD)",
                    "recommendation": "Gunakan tahun mulai: 1965 (untuk data lengkap energy + GDP)"
                }
            }
        
        result = {
            "success": True,
            "energyCount": 0,
            "gdpCount": 0,
            "message": "Data berhasil diambil dari API"
        }
        
        # Ensure data directory exists
        os.makedirs("data/raw", exist_ok=True)
        
        # Headers untuk menghindari 403 Forbidden
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        energy_df = None
        gdp_df = None
        
        # Fetch Energy Data
        if data_type in ['all', 'energy']:
            energy_url = "https://ourworldindata.org/grapher/fossil-fuel-primary-energy.csv?v=1&csvType=full&useColumnShortNames=true"
            energy_df = pd.read_csv(energy_url, storage_options=headers)
            
            # Filter Indonesia dan tahun
            energy_df = energy_df[energy_df["Entity"] == "Indonesia"]
            if "Year" in energy_df.columns:
                energy_df = energy_df[
                    (energy_df["Year"] >= start_year) & 
                    (energy_df["Year"] <= end_year)
                ]
        
        # Fetch GDP Data
        if data_type in ['all', 'gdp']:
            # Gunakan GDP constant 2015 US$ (NY.GDP.MKTP.KD) - lebih baik untuk time series
            # Data tersedia mulai 1960 (vs NY.GDP.MKTP.CD yang baru mulai 1967)
            # Constant price sudah adjusted for inflation
            gdp_url = "https://api.worldbank.org/v2/country/IDN/indicator/NY.GDP.MKTP.KD?format=json&per_page=100"
            gdp_json = requests.get(gdp_url, headers=headers).json()
            
            gdp_df = pd.DataFrame([
                {"year": int(d["date"]), "gdp": d["value"]}
                for d in gdp_json[1] 
                if d["value"] is not None and 
                   start_year <= int(d["date"]) <= end_year
            ])
            
            # Convert GDP to Billion USD untuk scale yang lebih comparable
            gdp_df["gdp"] = gdp_df["gdp"] / 1_000_000_000
        
        # PENTING: Align data jika fetch keduanya
        if data_type == 'all' and energy_df is not None and gdp_df is not None:
            # Cari tahun yang ada di kedua dataset (intersection)
            energy_years = set(energy_df["Year"].unique())
            gdp_years = set(gdp_df["year"].unique())
            common_years = sorted(energy_years.intersection(gdp_years))
            
            if not common_years:
                energy_list = sorted(list(energy_years)) if energy_years else []
                gdp_list = sorted(list(gdp_years)) if gdp_years else []
                return {
                    "success": False,
                    "message": f"Tidak ada tahun yang sama antara data energi ({min(energy_list) if energy_list else 'N/A'}-{max(energy_list) if energy_list else 'N/A'}) dan GDP ({min(gdp_list) if gdp_list else 'N/A'}-{max(gdp_list) if gdp_list else 'N/A'}). Silakan sesuaikan rentang tahun."
                }
            
            # Validasi: cek apakah ada cukup overlap dengan tahun yang diminta
            requested_years = set(range(start_year, end_year + 1))
            actual_coverage = len(set(common_years).intersection(requested_years))
            coverage_percentage = (actual_coverage / len(requested_years)) * 100 if requested_years else 0
            
            # Filter hanya tahun yang ada di kedua dataset
            energy_df = energy_df[energy_df["Year"].isin(common_years)]
            gdp_df = gdp_df[gdp_df["year"].isin(common_years)]
            
            # Informasi ke user jika ada data yang di-drop
            energy_dropped = len(energy_years) - len(common_years)
            gdp_dropped = len(gdp_years) - len(common_years)
            
            # Convert numpy/pandas types to Python native types for JSON serialization
            common_years_list = [int(y) for y in common_years]
            energy_only_list = [int(y) for y in sorted(list(energy_years - gdp_years))]
            gdp_only_list = [int(y) for y in sorted(list(gdp_years - energy_years))]
            
            # Pesan yang lebih informatif
            result["message"] = f"Data berhasil disesuaikan: {len(common_years)} tahun yang cocok ({min(common_years_list)}-{max(common_years_list)}). "
            
            if coverage_percentage < 100:
                result["message"] += f"Coverage: {coverage_percentage:.1f}% dari rentang yang diminta. "
            
            if energy_dropped > 0 or gdp_dropped > 0:
                warnings = []
                if energy_dropped > 0:
                    result["message"] += f"⚠️ {energy_dropped} tahun energi tidak ada GDP-nya. "
                    warnings.append(f"Data energi tersedia untuk {len(energy_years)} tahun, tapi {energy_dropped} tahun tidak memiliki data GDP")
                if gdp_dropped > 0:
                    result["message"] += f"⚠️ {gdp_dropped} tahun GDP tidak ada energi-nya. "
                    warnings.append(f"Data GDP tersedia untuk {len(gdp_years)} tahun, tapi {gdp_dropped} tahun tidak memiliki data energi")
                
                result["warnings"] = warnings
                result["alignment_info"] = {
                    "common_years": common_years_list,
                    "total_matched": int(len(common_years)),
                    "year_range": f"{int(min(common_years_list))}-{int(max(common_years_list))}",
                    "energy_only_years": energy_only_list[:10] if len(energy_only_list) > 10 else energy_only_list,
                    "gdp_only_years": gdp_only_list[:10] if len(gdp_only_list) > 10 else gdp_only_list,
                    "coverage_percentage": float(coverage_percentage)
                }
                
                # Jika coverage terlalu rendah, beri warning khusus
                if coverage_percentage < 50:
                    result["message"] += " ⚠️ WARNING: Coverage rendah, pertimbangkan sesuaikan rentang tahun."
        
        # Save data to CSV (for training)
        energy_records = 0
        gdp_records = 0
        
        if energy_df is not None:
            energy_df.to_csv("data/raw/energy.csv", index=False)
            result["energyCount"] = int(len(energy_df))
            energy_records = len(energy_df)
            
            # Save to MySQL
            try:
                save_energy_to_db(energy_df)
            except Exception as db_err:
                print(f"Warning: Failed to save energy to MySQL: {db_err}")
        
        if gdp_df is not None:
            gdp_df.to_csv("data/raw/gdp.csv", index=False)
            result["gdpCount"] = int(len(gdp_df))
            gdp_records = len(gdp_df)
            
            # Save to MySQL
            try:
                save_gdp_to_db(gdp_df)
            except Exception as db_err:
                print(f"Warning: Failed to save GDP to MySQL: {db_err}")
        
        # Save to history
        try:
            total_records = energy_records + gdp_records
            save_data_update_history(
                update_type='fetch_api',
                source=f"OWID Energy + World Bank GDP ({start_year}-{end_year})",
                records_added=0,
                records_updated=total_records,
                status='success',
                message=f"Energy: {energy_records} records, GDP: {gdp_records} records"
            )
        except Exception as hist_err:
            print(f"Warning: Failed to save update history: {hist_err}")
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching data: {str(e)}"
        }


def upload_data_from_files(energy_file=None, gdp_file=None):
    """
    Upload data dari file CSV atau Excel
    
    Args:
        energy_file: File object untuk data energi
        gdp_file: File object untuk data GDP
    """
    try:
        result = {
            "success": True,
            "energyCount": 0,
            "gdpCount": 0,
            "message": "File berhasil diupload"
        }
        
        # Ensure data directory exists
        os.makedirs("data/raw", exist_ok=True)
        
        energy_df = None
        gdp_df = None
        
        # Process Energy File
        if energy_file:
            filename = energy_file.filename.lower()
            
            try:
                if filename.endswith('.csv'):
                    # Try different delimiters and skip metadata rows
                    energy_df = None
                    errors = []
                    
                    # Reset file pointer
                    energy_file.seek(0)
                    
                    # Try comma first (default)
                    try:
                        energy_df = pd.read_csv(energy_file, sep=',', on_bad_lines='skip')
                    except Exception as e1:
                        errors.append(f"Comma: {str(e1)}")
                        
                        # Try semicolon
                        energy_file.seek(0)
                        try:
                            energy_df = pd.read_csv(energy_file, sep=';', on_bad_lines='skip')
                        except Exception as e2:
                            errors.append(f"Semicolon: {str(e2)}")
                            
                            # Try tab
                            energy_file.seek(0)
                            try:
                                energy_df = pd.read_csv(energy_file, sep='\t', on_bad_lines='skip')
                            except Exception as e3:
                                errors.append(f"Tab: {str(e3)}")
                                
                                # Try auto-detect with python engine
                                energy_file.seek(0)
                                try:
                                    energy_df = pd.read_csv(energy_file, sep=None, engine='python', on_bad_lines='skip')
                                except Exception as e4:
                                    errors.append(f"Auto-detect: {str(e4)}")
                    
                    if energy_df is None:
                        raise ValueError(
                            f"Gagal membaca file CSV. File mungkin memiliki format yang tidak standar. "
                            f"Pastikan file adalah CSV yang valid dengan delimiter koma (,) atau titik koma (;). "
                            f"Detail error: {'; '.join(errors[:2])}"
                        )
                    
                elif filename.endswith(('.xlsx', '.xls')):
                    energy_df = pd.read_excel(energy_file)
                else:
                    raise ValueError("Format file energi tidak didukung. Gunakan CSV atau Excel (.xlsx/.xls)")
            except Exception as e:
                if isinstance(e, ValueError):
                    raise
                raise ValueError(f"Error membaca file energi: {str(e)}")
            
            # Validasi kolom minimal
            # Normalize column names: lowercase dan replace spaces/special chars dengan underscore
            energy_df.columns = [
                col.lower()
                .replace(' ', '_')
                .replace('(', '')
                .replace(')', '')
                .replace('-', '_')
                for col in energy_df.columns
            ]
            
            # AUTO FILTER: Jika ada kolom Entity/Country, filter hanya Indonesia
            entity_col = None
            for col in ['entity', 'country', 'country_name', 'nation']:
                if col in energy_df.columns:
                    entity_col = col
                    break
            
            if entity_col:
                # Filter Indonesia
                indonesia_data = energy_df[
                    energy_df[entity_col].str.lower().str.contains('indonesia', na=False)
                ]
                
                if len(indonesia_data) > 0:
                    energy_df = indonesia_data
                    print(f"✓ Auto-filtered {len(energy_df)} records untuk Indonesia dari kolom '{entity_col}'")
                else:
                    print(f"⚠️ Warning: Kolom '{entity_col}' ditemukan tapi tidak ada data Indonesia. Menggunakan semua data.")
            else:
                print(f"ℹ️ Info: Tidak ada kolom Entity/Country. Menggunakan semua data sebagai data Indonesia.")
            
            if 'year' not in energy_df.columns:
                raise ValueError("File energi harus memiliki kolom 'year' atau 'Year'")
            
            # Cek kolom value dengan berbagai variasi nama
            value_col = None
            possible_value_cols = [
                'value', 'energy', 'fossil_fuels', 'fossil_fuels_twh', 
                'fossil_fuel', 'fossil_fuels__twh', 'consumption',
                'energy_consumption', 'total_energy'
            ]
            
            for col in possible_value_cols:
                if col in energy_df.columns:
                    value_col = col
                    break
            
            if not value_col:
                # Show available columns to help user
                available_cols = ', '.join(energy_df.columns)
                raise ValueError(
                    f"File energi harus memiliki kolom nilai energi. "
                    f"Kolom yang dicari: {', '.join(possible_value_cols[:5])}. "
                    f"Kolom tersedia di file: {available_cols}"
                )
            
            # Rename kolom ke format standar
            energy_df = energy_df.rename(columns={
                'year': 'Year',
                value_col: 'fossil_fuels__twh'
            })
            
            # Keep only needed columns
            energy_df = energy_df[['Year', 'fossil_fuels__twh']].copy()
            energy_df.columns = ['Year', 'fossil_fuels__twh']
            
            print(f"✓ Energy data: {len(energy_df)} tahun ({energy_df['Year'].min()}-{energy_df['Year'].max()})")
            print(f"✓ Kolom value: '{value_col}' → 'fossil_fuels__twh'")
        
        # Process GDP File
        if gdp_file:
            filename = gdp_file.filename.lower()
            
            try:
                if filename.endswith('.csv'):
                    # World Bank format often has metadata rows at top
                    # Try skipping rows and detect format
                    gdp_file.seek(0)
                    
                    # Read first few lines to detect format
                    sample = gdp_file.read(500).decode('utf-8', errors='ignore')
                    gdp_file.seek(0)
                    
                    # Check if World Bank format (has "Country Name","Country Code" etc)
                    skip_rows = 0
                    if 'Country Name' in sample or 'Country Code' in sample:
                        # World Bank format - skip metadata rows (usually 3-4 rows)
                        skip_rows = 4
                        print(f"ℹ️ Detected World Bank format, skipping {skip_rows} metadata rows")
                    
                    gdp_df = pd.read_csv(gdp_file, skiprows=skip_rows, on_bad_lines='skip')
                    
                elif filename.endswith(('.xlsx', '.xls')):
                    gdp_df = pd.read_excel(gdp_file)
                else:
                    raise ValueError("Format file GDP tidak didukung. Gunakan CSV atau Excel")
            except Exception as e:
                if isinstance(e, ValueError):
                    raise
                raise ValueError(f"Error membaca file GDP: {str(e)}")
            
            # Normalize column names
            gdp_df.columns = [
                str(col).lower()
                .replace(' ', '_')
                .replace('(', '')
                .replace(')', '')
                .replace('-', '_')
                .replace('"', '')
                for col in gdp_df.columns
            ]
            
            print(f"ℹ️ GDP file columns: {list(gdp_df.columns[:10])}... ({len(gdp_df.columns)} total)")
            
            # Check if World Bank wide format (years as columns: 1960, 1961, etc)
            year_columns = [col for col in gdp_df.columns if col.isdigit() and len(col) == 4]
            
            if len(year_columns) > 10:
                # Wide format - transform to long format
                print(f"✓ Detected wide format with {len(year_columns)} year columns. Transforming to long format...")
                
                # Find identifier columns (country name, code, indicator, etc)
                id_cols = [col for col in gdp_df.columns if not col.isdigit()]
                
                # Melt to long format
                gdp_long = pd.melt(
                    gdp_df, 
                    id_vars=id_cols,
                    value_vars=year_columns,
                    var_name='year',
                    value_name='gdp'
                )
                
                # Filter Indonesia before converting year
                entity_col = None
                for col in ['country_name', 'country', 'entity', 'country_code']:
                    if col in gdp_long.columns:
                        entity_col = col
                        break
                
                if entity_col:
                    indonesia_data = gdp_long[
                        gdp_long[entity_col].astype(str).str.lower().str.contains('indonesia|idn', na=False, regex=True)
                    ]
                    
                    if len(indonesia_data) > 0:
                        gdp_long = indonesia_data
                        print(f"✓ Auto-filtered Indonesia from '{entity_col}' column")
                    else:
                        print(f"⚠️ Warning: No Indonesia data found in '{entity_col}'")
                
                # Convert year to int
                gdp_long['year'] = gdp_long['year'].astype(int)
                
                # Drop rows with missing GDP values
                gdp_long = gdp_long.dropna(subset=['gdp'])
                
                # Convert GDP to Billion USD (same as API fetch)
                gdp_long['gdp'] = gdp_long['gdp'] / 1_000_000_000
                
                # Keep only year and gdp
                gdp_df = gdp_long[['year', 'gdp']].copy()
                
                print(f"✓ Transformed to long format: {len(gdp_df)} records")
                print(f"✓ Converted to Billion USD")
                
            else:
                # Standard long format - process normally
                # AUTO FILTER: Jika ada kolom Entity/Country, filter hanya Indonesia  
                entity_col = None
                for col in ['entity', 'country', 'country_name', 'nation', 'country_code']:
                    if col in gdp_df.columns:
                        entity_col = col
                        break
                
                if entity_col:
                    # Filter Indonesia (by name or code IDN/ID)
                    indonesia_data = gdp_df[
                        gdp_df[entity_col].astype(str).str.lower().str.contains('indonesia|idn|id', na=False, regex=True)
                    ]
                    
                    if len(indonesia_data) > 0:
                        gdp_df = indonesia_data
                        print(f"✓ Auto-filtered {len(gdp_df)} records untuk Indonesia dari kolom '{entity_col}'")
                    else:
                        print(f"⚠️ Warning: Kolom '{entity_col}' ditemukan tapi tidak ada data Indonesia. Menggunakan semua data.")
                
                # Find year column
                year_col = None
                for col in ['year', 'time', 'date', 'tahun']:
                    if col in gdp_df.columns:
                        year_col = col
                        break
                        
                if not year_col:
                    raise ValueError(f"File GDP harus memiliki kolom 'year'. Kolom tersedia: {', '.join(gdp_df.columns)}")
                
                # Find GDP value column
                gdp_col = None
                for col in ['gdp', 'value', 'gdp_value', 'gdp_current', 'gdp_constant', 'gdp_usd']:
                    if col in gdp_df.columns:
                        gdp_col = col
                        break
                        
                if not gdp_col:
                    raise ValueError(f"File GDP harus memiliki kolom 'gdp' atau 'value'. Kolom tersedia: {', '.join(gdp_df.columns)}")
                
                # Rename to standard format
                gdp_df = gdp_df.rename(columns={
                    year_col: 'year',
                    gdp_col: 'gdp'
                })
                
                # Convert GDP to Billion USD (same as API fetch)
                gdp_df['gdp'] = gdp_df['gdp'] / 1_000_000_000
                
                # Keep only needed columns
                gdp_df = gdp_df[['year', 'gdp']].copy()
            
            print(f"✓ GDP data: {len(gdp_df)} tahun ({int(gdp_df['year'].min())}-{int(gdp_df['year'].max())})")
            print(f"✓ Unit: Billion USD (converted from original)")
            print(f"✓ Sample values: {gdp_df.head(3).to_dict('records')}")
        
        if not energy_file and not gdp_file:
            raise ValueError("Minimal satu file harus diupload")
        
        # PENTING: Jika upload keduanya, align datanya
        if energy_df is not None and gdp_df is not None:
            # Cari tahun yang ada di kedua dataset
            energy_years = set(energy_df["Year"].unique())
            gdp_years = set(gdp_df["year"].unique())
            common_years = sorted(energy_years.intersection(gdp_years))
            
            if not common_years:
                raise ValueError(
                    f"Tidak ada tahun yang sama antara file energi ({min(energy_years)}-{max(energy_years)}) "
                    f"dan GDP ({min(gdp_years)}-{max(gdp_years)}). "
                    "Pastikan kedua file memiliki tahun yang overlap."
                )
            
            # Filter hanya tahun yang ada di kedua dataset
            energy_df = energy_df[energy_df["Year"].isin(common_years)]
            gdp_df = gdp_df[gdp_df["year"].isin(common_years)]
            
            # Info ke user
            energy_dropped = len(energy_years) - len(common_years)
            gdp_dropped = len(gdp_years) - len(common_years)
            
            # Convert to Python native types
            common_years_list = [int(y) for y in common_years]
            
            if energy_dropped > 0 or gdp_dropped > 0:
                warnings = []
                result["message"] = f"Data disesuaikan: {len(common_years)} tahun yang cocok ({min(common_years_list)}-{max(common_years_list)}). "
                
                if energy_dropped > 0:
                    result["message"] += f"⚠️ {energy_dropped} tahun energi tidak ada GDP-nya. "
                    warnings.append(f"{energy_dropped} tahun energi tidak memiliki data GDP")
                if gdp_dropped > 0:
                    result["message"] += f"⚠️ {gdp_dropped} tahun GDP tidak ada energi-nya. "
                    warnings.append(f"{gdp_dropped} tahun GDP tidak memiliki data energi")
                
                result["warnings"] = warnings
                result["alignment_info"] = {
                    "total_matched": int(len(common_years)),
                    "year_range": f"{int(min(common_years_list))}-{int(max(common_years_list))}"
                }
        
        # Save files to CSV (for training)
        energy_records = 0
        gdp_records = 0
        
        if energy_df is not None:
            energy_df.to_csv("data/raw/energy.csv", index=False)
            result["energyCount"] = len(energy_df)
            energy_records = len(energy_df)
            
            # Save to MySQL
            try:
                save_energy_to_db(energy_df)
            except Exception as db_err:
                print(f"Warning: Failed to save energy to MySQL: {db_err}")
        
        if gdp_df is not None:
            gdp_df.to_csv("data/raw/gdp.csv", index=False)
            result["gdpCount"] = len(gdp_df)
            gdp_records = len(gdp_df)
            
            # Save to MySQL
            try:
                save_gdp_to_db(gdp_df)
            except Exception as db_err:
                print(f"Warning: Failed to save GDP to MySQL: {db_err}")
        
        # Save to history
        try:
            total_records = energy_records + gdp_records
            filenames = []
            if energy_file:
                filenames.append(energy_file.filename)
            if gdp_file:
                filenames.append(gdp_file.filename)
            
            save_data_update_history(
                update_type='manual_upload',
                source=', '.join(filenames),
                records_added=0,
                records_updated=total_records,
                status='success',
                message=f"Energy: {energy_records} records, GDP: {gdp_records} records"
            )
        except Exception as hist_err:
            print(f"Warning: Failed to save update history: {hist_err}")
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error uploading file: {str(e)}"
        }


def get_data_stats():
    """
    Get statistik data energi dan GDP
    """
    try:
        stats = {
            "energyCount": 0,
            "gdpCount": 0,
            "lastUpdate": "-"
        }
        
        # Check energy file
        energy_path = "data/raw/energy.csv"
        if os.path.exists(energy_path):
            energy_df = pd.read_csv(energy_path)
            stats["energyCount"] = len(energy_df)
            stats["lastUpdate"] = datetime.fromtimestamp(
                os.path.getmtime(energy_path)
            ).strftime("%d %b %Y %H:%M")
        
        # Check GDP file
        gdp_path = "data/raw/gdp.csv"
        if os.path.exists(gdp_path):
            gdp_df = pd.read_csv(gdp_path)
            stats["gdpCount"] = len(gdp_df)
            
            # Update last update time if GDP is newer
            if os.path.exists(gdp_path):
                gdp_time = datetime.fromtimestamp(os.path.getmtime(gdp_path))
                if stats["lastUpdate"] == "-" or gdp_time > datetime.strptime(stats["lastUpdate"], "%d %b %Y %H:%M"):
                    stats["lastUpdate"] = gdp_time.strftime("%d %b %Y %H:%M")
        
        return stats
        
    except Exception as e:
        return {
            "energyCount": 0,
            "gdpCount": 0,
            "lastUpdate": "-"
        }


def get_energy_data(limit=10):
    """
    Get preview data energi
    """
    try:
        energy_path = "data/raw/energy.csv"
        if not os.path.exists(energy_path):
            return []
        
        energy_df = pd.read_csv(energy_path)
        
        # Sort by year descending
        if "Year" in energy_df.columns:
            energy_df = energy_df.sort_values("Year", ascending=False)
        
        # Get limited records
        energy_df = energy_df.head(limit)
        
        # Prepare data for frontend
        records = []
        for _, row in energy_df.iterrows():
            # Coba berbagai nama kolom yang mungkin untuk nilai energi
            value = row.get("fossil_fuels__twh", row.get("fossil_fuels", row.get("value", 0)))
            
            records.append({
                "year": row.get("Year", row.get("year", "-")),
                "country": row.get("Entity", "Indonesia"),
                "value": value,
                "unit": "TWh",  # Tambahkan info satuan
                "updated": datetime.now().strftime("%d %b %Y")
            })
        
        return records
        
    except Exception as e:
        print(f"Error getting energy data: {str(e)}")
        return []


def get_gdp_data(limit=10):
    """
    Get preview data GDP
    """
    try:
        gdp_path = "data/raw/gdp.csv"
        if not os.path.exists(gdp_path):
            return []
        
        gdp_df = pd.read_csv(gdp_path)
        
        # Sort by year descending
        if "year" in gdp_df.columns:
            gdp_df = gdp_df.sort_values("year", ascending=False)
        
        # Get limited records
        gdp_df = gdp_df.head(limit)
        
        # Prepare data for frontend
        records = []
        for _, row in gdp_df.iterrows():
            records.append({
                "year": row.get("year", "-"),
                "country": "Indonesia",
                "value": row.get("gdp", 0),
                "unit": "Billion USD",  # Tambahkan info satuan
                "updated": datetime.now().strftime("%d %b %Y")
            })
        
        return records
        
    except Exception as e:
        print(f"Error getting GDP data: {str(e)}")
        return []


def preview_api_data():
    # AMBIL LANGSUNG DARI API (BUKAN FILE)
    energy_url = "https://ourworldindata.org/grapher/fossil-fuel-primary-energy.csv?v=1&csvType=full&useColumnShortNames=true"
    energy_df = pd.read_csv(energy_url)

    energy_preview = (
        energy_df[energy_df["Entity"] == "Indonesia"]
        .sort_values("Year", ascending=False)
        .head(5)
        .to_dict(orient="records")
    )

    gdp_url = "https://api.worldbank.org/v2/country/IDN/indicator/NY.GDP.MKTP.CD?format=json"
    gdp_json = requests.get(gdp_url).json()

    gdp_preview = [
        {"year": d["date"], "gdp": d["value"]}
        for d in gdp_json[1]
        if d["value"] is not None
    ][:5]

    return jsonify({
        "energy_api_preview": energy_preview,
        "gdp_api_preview": gdp_preview
    })

