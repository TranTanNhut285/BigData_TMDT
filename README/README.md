# Hệ Thống Phân Tích Big Data và Gợi Ý Sản Phẩm TMĐT

Hệ thống xử lý dữ liệu lớn với Apache Spark, Machine Learning gợi ý sản phẩm (ALS), phân cụm (KMeans), và trực quan hóa web (Streamlit).

## 🎯 Tính năng chính
- **Xử lý phân tán:** Apache Spark ETL, hỗ trợ HDFS/Ceph/GlusterFS
- **Machine Learning:** ALS recommender, Item similarity, KMeans clustering
- **Trực quan hóa:** Streamlit web app với giao diện tiếng Việt
- **Scalable:** Từ demo nhỏ đến triệu records trên cluster

## 🛠️ Công nghệ
- **Big Data:** Apache Spark, PySpark
- **ML:** Spark MLlib (ALS, KMeans)
- **Visualization:** Streamlit, Seaborn, Matplotlib
- **Storage:** HDFS / Local (configurable)

## 📁 Cấu trúc Project
```
DOAN/
  ├── app/           # Streamlit web interface
  ├── spark_jobs/    # Spark ETL + ML jobs
  ├── data/          # Input data (CSV)
  ├── artifacts/     # Output results
  └── utils/         # Config helpers
```

## 🚀 Cài đặt và Chạy

### Yêu cầu
- Python 3.10+
- Java JDK 8+ (cho Spark)

### Cài đặt
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Chạy toàn bộ hệ thống
```powershell
# Kích hoạt môi trường
.venv\Scripts\Activate.ps1

# Chạy tất cả Spark jobs
.\run_all.ps1

# Khởi động web app
streamlit run .\app\streamlit_app.py
```

Truy cập: http://localhost:8501

## ⚙️ Cấu hình Storage (Tùy chọn)

**Local (mặc định):** Đọc từ thư mục `data/`

**HDFS/Distributed:**
```powershell
$env:DATA_BACKEND = "hdfs"
$env:HDFS_URL = "hdfs://namenode:9000"
```

## 🔄 Pipeline Xử Lý

```
1. ETL (prepare_data.py)
   └─> Thống kê: rating distribution, top products, category analysis

2. ML Training (train_recommender.py)
   ├─> ALS Recommender: Top-K sản phẩm cho mỗi user
   └─> Item Similarity: Cosine similarity giữa các sản phẩm

3. Clustering (product_clustering.py)
   └─> KMeans: Nhóm sản phẩm theo đặc tính

4. Visualization (streamlit_app.py)
   └─> Web dashboard với 3 tab: Gợi ý User, Sản phẩm tương tự, Phân tích
```

## 🎨 Giao Diện Web (Streamlit)

### Tab 1: Gợi ý cho người dùng
- Chọn user_id → Xem Top-K sản phẩm phù hợp
- Điểm dự đoán từ ALS model
- Biểu đồ trực quan

### Tab 2: Sản phẩm tương tự
- Chọn product_id → Tìm sản phẩm giống nhau
- Độ tương đồng cosine similarity
- Hữu ích cho cross-selling

### Tab 3: Phân tích tổng quan
- Phân phối điểm đánh giá
- Top sản phẩm nổi bật
- Phân tích theo danh mục

**Tính năng:** Giao diện tiếng Việt, slider điều chỉnh, responsive design

## 📊 Kết Quả Demo

**Dữ liệu mẫu:** 5 users × 10 products × 26 ratings

**Kết quả ML:**
- ALS Model: 10 latent factors
- Top-5 recommendations cho mỗi user
- Item similarity matrix
- Product clustering

**Ví dụ gợi ý cho User 1:**
```
1. Noise Cancelling Headphones (4.97★)
2. Mechanical Keyboard (4.92★)
3. Data Science Book (4.68★)
```

## 🔧 Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| Java errors | Đặt `JAVA_HOME` và thêm vào PATH |
| Streamlit không hiển thị | Chạy Spark jobs trước để tạo artifacts |
| Chart quá lớn | Dùng slider trong sidebar để điều chỉnh |

## 📚 Tài Liệu Thêm

- `GIAI_THICH_GOI_Y.md` - Chi tiết thuật toán ALS và Item Similarity
- `NOI_DUNG_THUYET_TRINH.md` - Nội dung thuyết trình project (20 slides)

## 📄 License

Open source - Tự do sử dụng và chỉnh sửa
