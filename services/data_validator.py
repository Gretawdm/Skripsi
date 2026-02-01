import pandas as pd
import os


def validate_data_compatibility():
    """
    Validasi kompatibilitas data energi dan GDP untuk training model ARIMAX
    
    Returns:
        dict: Status validasi dengan detail informasi
    """
    try:
        # Check if files exist
        energy_path = "data/raw/energy.csv"
        gdp_path = "data/raw/gdp.csv"
        
        if not os.path.exists(energy_path):
            return {
                "valid": False,
                "message": "File energy.csv tidak ditemukan",
                "suggestion": "Lakukan fetch data atau upload file terlebih dahulu"
            }
        
        if not os.path.exists(gdp_path):
            return {
                "valid": False,
                "message": "File gdp.csv tidak ditemukan",
                "suggestion": "Lakukan fetch data atau upload file terlebih dahulu"
            }
        
        # Load data
        energy_df = pd.read_csv(energy_path)
        gdp_df = pd.read_csv(gdp_path)
        
        # Identify year columns
        energy_year_col = None
        for col in ["Year", "year"]:
            if col in energy_df.columns:
                energy_year_col = col
                break
        
        gdp_year_col = None
        for col in ["year", "Year"]:
            if col in gdp_df.columns:
                gdp_year_col = col
                break
        
        if not energy_year_col or not gdp_year_col:
            return {
                "valid": False,
                "message": "Kolom tahun tidak ditemukan",
                "energy_columns": list(energy_df.columns),
                "gdp_columns": list(gdp_df.columns)
            }
        
        # Get years
        energy_years = set(energy_df[energy_year_col].dropna().unique())
        gdp_years = set(gdp_df[gdp_year_col].dropna().unique())
        
        # Find common years
        common_years = sorted(energy_years.intersection(gdp_years))
        energy_only = sorted(energy_years - gdp_years)
        gdp_only = sorted(gdp_years - energy_years)
        
        # Validation checks
        if not common_years:
            return {
                "valid": False,
                "message": "Tidak ada tahun yang sama antara data energi dan GDP",
                "energy_range": f"{min(energy_years)}-{max(energy_years)}" if energy_years else "N/A",
                "gdp_range": f"{min(gdp_years)}-{max(gdp_years)}" if gdp_years else "N/A",
                "suggestion": "Sesuaikan rentang tahun saat fetch/upload data"
            }
        
        if len(common_years) < 10:
            return {
                "valid": False,
                "message": f"Data tidak cukup untuk training: hanya {len(common_years)} tahun yang cocok",
                "common_years": common_years,
                "suggestion": "Minimal 10 tahun data diperlukan. Perluas rentang tahun."
            }
        
        # Jika valid
        result = {
            "valid": True,
            "message": f"Data kompatibel: {len(common_years)} tahun cocok untuk training",
            "summary": {
                "total_energy_years": len(energy_years),
                "total_gdp_years": len(gdp_years),
                "matched_years": len(common_years),
                "year_range": f"{min(common_years)}-{max(common_years)}"
            }
        }
        
        # Tambahkan warning jika ada data yang tidak match
        if energy_only or gdp_only:
            warnings = []
            if energy_only:
                warnings.append(f"{len(energy_only)} tahun energi tanpa GDP: {energy_only[:5]}{'...' if len(energy_only) > 5 else ''}")
            if gdp_only:
                warnings.append(f"{len(gdp_only)} tahun GDP tanpa energi: {gdp_only[:5]}{'...' if len(gdp_only) > 5 else ''}")
            
            result["warnings"] = warnings
            result["message"] += f" (ada {len(energy_only) + len(gdp_only)} tahun yang tidak match)"
        
        return result
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error validasi data: {str(e)}"
        }


def get_data_alignment_report():
    """
    Generate detailed report tentang alignment data
    """
    try:
        energy_df = pd.read_csv("data/raw/energy.csv")
        gdp_df = pd.read_csv("data/raw/gdp.csv")
        
        # Identify year columns
        energy_year_col = "Year" if "Year" in energy_df.columns else "year"
        gdp_year_col = "year" if "year" in gdp_df.columns else "Year"
        
        energy_years = sorted(energy_df[energy_year_col].dropna().unique())
        gdp_years = sorted(gdp_df[gdp_year_col].dropna().unique())
        
        common_years = sorted(set(energy_years).intersection(set(gdp_years)))
        
        return {
            "energy": {
                "total_records": len(energy_df),
                "total_years": len(energy_years),
                "year_range": f"{min(energy_years)}-{max(energy_years)}" if energy_years else "N/A",
                "years": energy_years
            },
            "gdp": {
                "total_records": len(gdp_df),
                "total_years": len(gdp_years),
                "year_range": f"{min(gdp_years)}-{max(gdp_years)}" if gdp_years else "N/A",
                "years": gdp_years
            },
            "alignment": {
                "common_years": common_years,
                "total_matched": len(common_years),
                "year_range": f"{min(common_years)}-{max(common_years)}" if common_years else "N/A",
                "energy_only_years": sorted(set(energy_years) - set(gdp_years)),
                "gdp_only_years": sorted(set(gdp_years) - set(energy_years))
            }
        }
        
    except Exception as e:
        return {
            "error": str(e)
        }
