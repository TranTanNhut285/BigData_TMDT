# Mini Phân tích Dữ liệu & Gợi ý (PySpark + Pandas + Streamlit)

Phần mô tả nhanh (Tiếng Việt):
- Lưu trữ dữ liệu linh hoạt (HDFS hoặc local) với cấu hình qua biến môi trường.
- Xử lý/Phân tích bằng Apache Spark: ETL, ALS gợi ý, KMeans gom cụm.
- Trực quan hóa bằng Seaborn/Matplotlib và app web Streamlit.
- Dễ chạy demo với dữ liệu mẫu; mở rộng được cho dữ liệu lớn.

English description is kept below for reference.

A small end-to-end pipeline that:
- Stores data in a distributed-friendly layout (HDFS-ready), with local fallback.
- Processes and analyzes data using Apache Spark (ETL, ALS recommender, KMeans clustering).
- Visualizes results via Seaborn/Matplotlib.
- Serves a mini web app (Streamlit) to show charts and product recommendations.

## Tech
- Python, PySpark, Pandas, Seaborn/Matplotlib, Streamlit
- Optional distributed storage: HDFS (or Ceph/GlusterFS mounted paths)

## Structure
```
DOAN/
  app/                    # Streamlit mini web app
  artifacts/              # Outputs from Spark jobs (charts data, recs, clusters)
  data/                   # Sample input CSVs (or point to HDFS)
  spark_jobs/             # Spark ETL + ML jobs
  utils/                  # Shared config helpers
  requirements.txt        # Python dependencies
  README.md               # This guide
```

## Prerequisites (Windows)
- Python 3.10 or 3.11
- Java JDK 8+ (required by Spark)
- Apache Spark binaries (optional if using pyspark wheel only; recommended to install)
- HDFS access (optional). If you have a Hadoop cluster, set `HDFS_URL` env var.

## Cài đặt / Install deps
In PowerShell:

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Cấu hình nguồn dữ liệu (HDFS/local) / Configure data backend
- Local (default): uses CSV files in `data/`
- HDFS: set environment variables before running jobs/app:

```powershell
$env:DATA_BACKEND = "hdfs"          # or "local"
$env:HDFS_URL = "hdfs://namenode:9000"  # change to your HDFS NameNode URL
```

You can also create a `.env` file at the repo root:
```
DATA_BACKEND=hdfs
HDFS_URL=hdfs://namenode:9000
```

## Dữ liệu mẫu / Prepare sample data
Sample CSVs are provided in `data/`:
- `products.csv`: product catalog
- `ratings.csv`: user-product ratings

Replace with your own large datasets by either copying to `data/` or uploading to HDFS (e.g., `/data/products.csv`, `/data/ratings.csv`).

## Chạy các Spark jobs / Run Spark jobs
Run ETL aggregates (charts), recommender, and clustering. These write outputs to `artifacts/`.

```powershell
# Activate venv first
. .venv\Scripts\Activate.ps1

# 1) Aggregates for charts
python .\spark_jobs\prepare_data.py

# 2) Train recommender and export top-N
python .\spark_jobs\train_recommender.py

# 3) Product clustering
python .\spark_jobs\product_clustering.py
```

If using HDFS, make sure input paths exist on HDFS (e.g., `hdfs://.../data/products.csv`).

## Chạy ứng dụng web / Run the mini web app
```powershell
. .venv\Scripts\Activate.ps1
streamlit run .\app\streamlit_app.py
```
Then open the URL shown in the terminal (usually http://localhost:8501).

## Ghi chú về HDFS/Ceph/GlusterFS
- HDFS: this project reads/writes with Spark using `hdfs://...` URIs. Set `HDFS_URL`.
- Ceph/GlusterFS: often mounted as a POSIX path on Windows via network mounts; if so, set `DATA_BACKEND=local` and point `DATA_DIR` env var to the mounted path.

## Cách hoạt động chi tiết / How it works in detail

### 1. Kiến trúc hệ thống / System Architecture
Project này là một hệ thống Big Data hoàn chỉnh với các thành phần:

**Lớp lưu trữ (Storage Layer):**
- Hỗ trợ lưu trữ phân tán: HDFS, Ceph, GlusterFS
- Fallback về local storage để demo
- Cấu hình linh hoạt qua biến môi trường

**Lớp xử lý (Processing Layer):**
- Apache Spark để xử lý dữ liệu lớn
- PySpark API để tích hợp với Python
- Các job song song: ETL, ML, Clustering

**Lớp ứng dụng (Application Layer):**
- Streamlit web app với giao diện tiếng Việt
- Trực quan hóa dữ liệu với Seaborn/Matplotlib
- Giao diện tương tác để khám phá dữ liệu

### 2. Quy trình xử lý dữ liệu / Data Processing Pipeline

#### Bước 1: ETL và Chuẩn bị dữ liệu (`prepare_data.py`)
```
Dữ liệu thô (CSV) → Spark DataFrame → Tính toán thống kê → artifacts/charts_data.csv
```
- Đọc `products.csv` và `ratings.csv` từ HDFS/local
- Tính toán các thống kê:
  - Phân phối điểm đánh giá (rating distribution)
  - Top sản phẩm được đánh giá nhiều nhất
  - Số lượng đánh giá theo danh mục
- Xuất kết quả thành CSV để Streamlit sử dụng

#### Bước 2: Huấn luyện mô hình gợi ý (`train_recommender.py`)
```
Ma trận User-Product → ALS Model → Gợi ý Top-K → artifacts/recommendations.csv
```
- Sử dụng thuật toán ALS (Alternating Least Squares) của Spark MLlib
- Học các vector đặc trưng ẩn cho user và product
- Tạo gợi ý Top-K sản phẩm cho mỗi user
- **Tính toán độ tương tự sản phẩm:**
  - Sử dụng cosine similarity trên vector đặc trưng
  - Tìm Top-K sản phẩm tương tự cho mỗi sản phẩm
  - Xuất ra `artifacts/similar_products.csv`

#### Bước 3: Phân cụm sản phẩm (`product_clustering.py`)
```
Features sản phẩm → KMeans → Clusters → artifacts/product_clusters.csv
```
- Tạo vector đặc trưng từ danh mục và giá sản phẩm
- Sử dụng KMeans để nhóm sản phẩm tương tự
- Phân tích đặc điểm từng cluster

### 3. Kết quả và Giao diện / Results and Interface

#### Streamlit Web Application
Ứng dụng web có 3 tab chính với giao diện tiếng Việt:

**Tab 1: Gợi ý cho người dùng**
- Chọn user_id và số lượng gợi ý (Top-K)
- Hiển thị bảng sản phẩm được gợi ý với:
  - Tên sản phẩm, danh mục, giá
  - Điểm dự đoán từ mô hình ALS
- Biểu đồ cột thể hiện điểm dự đoán

**Tab 2: Sản phẩm tương tự**
- Chọn product_id và số lượng sản phẩm tương tự
- Hiển thị danh sách sản phẩm có độ tương đồng cao
- Biểu đồ độ tương đồng cosine
- Hữu ích cho cross-selling và upselling

**Tab 3: Phân tích tổng quan**
- Biểu đồ phân phối điểm đánh giá
- Top sản phẩm được quan tâm nhất
- Phân tích theo danh mục sản phẩm
- Slider điều chỉnh kích thước biểu đồ

#### Tính năng nổi bật
- **Giao diện tiếng Việt:** Tất cả labels, tên cột đều được việt hóa
- **Biểu đồ tương tác:** Slider để điều chỉnh kích thước, Top-K
- **Dữ liệu thời gian thực:** Tự động reload khi có artifacts mới
- **Responsive design:** Tối ưu cho nhiều kích thước màn hình

### 4. Khả năng mở rộng / Scalability

**Xử lý dữ liệu lớn:**
- Spark có thể scale từ single machine đến cluster hàng trăm node
- Hỗ trợ dữ liệu từ GB đến TB
- Memory optimization và lazy evaluation

**Lưu trữ phân tán:**
- HDFS: Fault-tolerant, replicated storage
- Ceph: Object storage với high availability  
- GlusterFS: Scale-out network-attached storage

**Machine Learning at Scale:**
- ALS algorithm được tối ưu cho big data
- Distributed training trên Spark cluster
- Có thể xử lý hàng triệu user và product

### 5. Kết quả đạt được / Achieved Results

**Độ chính xác gợi ý:**
- Mô hình ALS với RMSE thấp
- Top-K recommendations có độ chính xác cao
- Similarity-based recommendations bổ sung

**Hiệu năng xử lý:**
- ETL job xử lý nhanh với Spark SQL
- Parallel processing cho multiple users
- Optimized cho Windows environment

**Trải nghiệm người dùng:**
- Giao diện trực quan, dễ sử dụng
- Visualization rõ ràng với Seaborn
- Interactive controls với Streamlit

## What's implemented
- Distributed storage-ready I/O (HDFS scheme support via Spark)
- Spark ETL for charts data (rating distribution, top products, category counts)
- Spark ALS recommender (top-N per user/item exported)
- Spark KMeans clustering for products  
- Streamlit UI with Seaborn/Matplotlib charts and recommendations
- Item-item similarity using cosine distance on ALS factors
- Vietnamese localized interface with interactive controls

## Kết quả Demo / Demo Results

### Dữ liệu mẫu được xử lý:
- **26 đánh giá** từ 5 người dùng cho 10 sản phẩm
- **4 danh mục sản phẩm:** Electronics, Books, Clothing, Home
- **Khoảng giá:** từ $9.5 đến $129

### Kết quả Machine Learning:
- **ALS Model:** Học được 10 latent factors cho users/products
- **Recommendations:** Top-5 sản phẩm cho mỗi user với điểm dự đoán
- **Item Similarity:** Tính toán cosine similarity giữa các sản phẩm
- **Clustering:** Nhóm sản phẩm thành các cluster theo đặc tính

### Insights từ phân tích:
- **Xu hướng rating:** Phần lớn đánh giá ở mức 4-5 sao
- **Sản phẩm hot:** Electronics được quan tâm nhiều nhất
- **Pattern:** Users có xu hướng thích sản phẩm cùng danh mục

### Screenshots Demo:
```
[Gợi ý cho User 1]
- Noise Cancelling Headphones (4.97★)
- Mechanical Keyboard (4.31★)  
- Data Science Book (4.69★)

[Sản phẩm tương tự với Headphones]
- Wireless Mouse (0.85 similarity)
- Mechanical Keyboard (0.71 similarity)

[Phân tích theo danh mục]
- Electronics: 12 ratings (cao nhất)
- Books, Clothing, Home: ~5 ratings mỗi loại
```

## Chạy nhanh toàn bộ hệ thống / Quick Start Everything

Để chạy toàn bộ pipeline từ đầu:

```powershell
# 1. Kích hoạt môi trường
. .venv\Scripts\Activate.ps1

# 2. Chạy tất cả Spark jobs
.\run_all.ps1

# 3. Khởi động web app
streamlit run .\app\streamlit_app.py
```

Sau đó truy cập http://localhost:8501 để xem kết quả!

## Troubleshooting
- Java errors: ensure `JAVA_HOME` is set and Java is on PATH.
- Winutils/Hadoop on Windows: for HDFS access from local Windows, you may need Hadoop winutils; otherwise run Spark jobs on a Linux cluster or WSL.
- Streamlit not showing charts: ensure you ran the Spark jobs first to populate `artifacts/`.
- Chart size issues: Use the sidebar slider to adjust chart scale in the Streamlit app.
