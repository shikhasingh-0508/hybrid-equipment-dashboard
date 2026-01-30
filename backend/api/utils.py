import pandas as pd

def analyze_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        
        # Helper to calculate stats safely
        def get_stat(column, stat_type='mean'):
            if column in df.columns:
                val = getattr(df[column], stat_type)()
                return round(float(val), 2)
            return 0.0

        summary = {
            "total_records": int(len(df)),
            "avg_flowrate": get_stat('Flowrate', 'mean'),
            "avg_pressure": get_stat('Pressure', 'mean'),
            "avg_temperature": get_stat('Temperature', 'mean'),
            "max_pressure": get_stat('Pressure', 'max'),
            "max_temperature": get_stat('Temperature', 'max'),
            # 'type_dist' is the synchronized key for all charts
            "type_dist": df['Type'].value_counts().to_dict() if 'Type' in df.columns else {}
        }
        return summary
    except Exception as e:
        return {"error": str(e)}