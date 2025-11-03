# Requires: Python venv activated and dependencies installed
# Optional: set $env:DATA_BACKEND and $env:HDFS_URL prior to running

Write-Host "Đang chạy ETL (tổng hợp số liệu)..."
python .\spark_jobs\prepare_data.py
if ($LASTEXITCODE -ne 0) { Write-Error "prepare_data failed"; exit 1 }

Write-Host "Đang huấn luyện mô hình gợi ý ALS..."
python .\spark_jobs\train_recommender.py
if ($LASTEXITCODE -ne 0) { Write-Error "train_recommender failed"; exit 1 }

Write-Host "Đang gom cụm sản phẩm (KMeans)..."
python .\spark_jobs\product_clustering.py
if ($LASTEXITCODE -ne 0) { Write-Error "product_clustering failed"; exit 1 }

Write-Host "Hoàn tất mọi job. Khởi động giao diện: streamlit run .\app\streamlit_app.py"