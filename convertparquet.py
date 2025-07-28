import pandas as pd
# Carregue seu arquivo Excel uma última vez
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")
# Salve no formato Parquet
df.to_parquet("ProjectEmExcel_MKE.parquet")