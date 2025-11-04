# Yeu cau: Da kich hoat Python venv va cai dat dependencies
# Tuy chon: dat $env:DATA_BACKEND va $env:HDFS_URL truoc khi chay

Write-Host "Dang chay ETL (tong hop so lieu)..." -ForegroundColor Cyan
python -m spark_jobs.prepare_data
if ($LASTEXITCODE -ne 0) { Write-Error "ETL that bai"; exit 1 }

Write-Host "Dang huan luyen mo hinh goi y ALS..." -ForegroundColor Cyan
python -m spark_jobs.train_recommender
if ($LASTEXITCODE -ne 0) { Write-Error "Huan luyen that bai"; exit 1 }

Write-Host "Dang gom cum san pham (KMeans)..." -ForegroundColor Cyan
python -m spark_jobs.product_clustering
if ($LASTEXITCODE -ne 0) { Write-Error "Phan cum that bai"; exit 1 }

Write-Host "Hoan tat! Khoi dong giao dien bang: streamlit run .\app\streamlit_app.py" -ForegroundColor Green