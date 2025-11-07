import pandas as pd
import numpy as np

def clean_aampur(x):
    try:
        # Check for empty, NaN, or whitespace
        if pd.isna(x) or str(x).strip() == "":
            return "99"
        
        # Try to parse as float, then int
        val = int(float(x))
        # Format as two digits (e.g. 1 -> '01')
        return f"{val:02d}"
    except:
        # If conversion fails (like 'LA', 'MY', etc.)
        return "99"
    

def filter_dangerous_days(df, date_column='adate'):
    """
    กรองเฉพาะ 7 วันอันตรายในประเทศไทย
    - ปีใหม่: 29 ธ.ค. - 4 ม.ค. (7 วัน)
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    
    month = df[date_column].dt.month
    day = df[date_column].dt.day
    
    # กำหนดเงื่อนไข
    new_year = ((month == 12) & (day >= 20)) | ((month == 1) & (day <= 7))
    
    dangerous_mask = new_year
    
    return df[dangerous_mask].copy()

def filter_3_years(df, date_column='adate'):

    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    
    year = df[date_column].dt.year
    
    # กำหนดเงื่อนไข
    four_years = (year >= 2022)
    
    dangerous_mask = four_years
    
    return df[dangerous_mask].copy()


