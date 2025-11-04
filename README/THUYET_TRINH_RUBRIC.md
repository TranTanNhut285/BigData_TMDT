# Thuyết trình đáp ứng Rubric chấm điểm

## 1️⃣ Hệ thống lưu trữ phân tán (2 điểm)

- **Hỗ trợ HDFS, Ceph, GlusterFS:**
  - Project cho phép lưu trữ dữ liệu trên HDFS hoặc các hệ thống phân tán khác qua cấu hình biến môi trường (`DATA_BACKEND`, `HDFS_URL`).
  - Có thể chuyển đổi giữa lưu trữ local và phân tán mà không cần sửa code.
- **Tích hợp với Spark:**
  - Spark đọc/ghi trực tiếp từ HDFS, đảm bảo khả năng mở rộng cho dữ liệu lớn (GB-TB).
- **Ví dụ thực tế:**
  - Demo với file CSV local, nhưng có thể chạy trên cluster HDFS thật.

---

## 2️⃣ Xử lý và phân tích dữ liệu (4 điểm)

- **Xử lý ETL:**
  - Sử dụng Spark để tổng hợp, làm sạch, tính toán thống kê từ dữ liệu thô (ratings, products).
- **Phân tích thống kê:**
  - Phân phối điểm đánh giá, top sản phẩm, phân tích theo danh mục.
- **Machine Learning:**
  - Huấn luyện mô hình ALS recommender (gợi ý sản phẩm cá nhân hóa)
  - Tính độ tương đồng sản phẩm (item-item similarity)
  - Phân cụm sản phẩm bằng KMeans
- **Xử lý song song:**
  - Spark thực thi các job trên nhiều node, tối ưu cho dữ liệu lớn.
- **Ví dụ thực tế:**
  - Dự đoán Top-K sản phẩm cho từng user, tìm sản phẩm giống nhau, phân tích xu hướng rating.

---

## 3️⃣ Trực quan hóa kết quả (2 điểm)

- **Giao diện web Streamlit:**
  - Hiển thị bảng gợi ý, sản phẩm tương tự, phân tích tổng quan.
  - Tất cả labels, tên cột, chú thích đều tiếng Việt.
- **Biểu đồ trực quan:**
  - Sử dụng Seaborn/Matplotlib để vẽ biểu đồ cột, biểu đồ phân phối, biểu đồ danh mục.
  - Có slider điều chỉnh kích thước, Top-K, responsive cho nhiều thiết bị.
- **Ví dụ thực tế:**
  - Người dùng chọn user_id, xem gợi ý, xem sản phẩm tương tự, phân tích rating và danh mục.

---

## 4️⃣ Tính sáng tạo và hiệu quả của hệ thống (2 điểm)

- **Sáng tạo:**
  - Kết hợp 2 phương pháp gợi ý: ALS (user-based) + item similarity (item-based)
  - Giao diện hoàn toàn tiếng Việt, thân thiện người dùng
  - Có thể mở rộng thêm metadata, user profile, content-based
- **Hiệu quả:**
  - Xử lý nhanh với Spark, có thể scale lên hàng triệu records
  - Thiết kế module, dễ bảo trì, dễ mở rộng
  - Tối ưu cho cả Windows và Linux
- **Ví dụ thực tế:**
  - Demo chạy nhanh, kết quả trực quan, có thể chuyển đổi backend lưu trữ dễ dàng

---

## 🎯 Kết luận

Project đáp ứng đầy đủ 4 tiêu chí rubric:
- Lưu trữ phân tán
- Xử lý/phân tích dữ liệu lớn
- Trực quan hóa kết quả
- Sáng tạo, hiệu quả, dễ mở rộng

**Sẵn sàng trình bày và demo!**