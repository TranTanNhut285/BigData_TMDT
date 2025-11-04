# GIẢI THÍCH CHI TIẾT HỆ THỐNG GỢI Ý SẢN PHẨM

## Tổng quan
Hệ thống sử dụng 2 phương pháp gợi ý chính:
1. **Gợi ý cho người dùng (User-based)**: Dự đoán sản phẩm nào phù hợp với từng user
2. **Gợi ý sản phẩm tương tự (Item-based)**: Tìm sản phẩm giống nhau để cross-sell

---

## PHẦN 1: GỢI Ý CHO NGƯỜI DÙNG (ALS Algorithm)

### Bước 1: Dữ liệu đầu vào
Bảng `ratings.csv` chứa lịch sử đánh giá:
```
user_id | product_id | rating
   1    |     2      |   5
   1    |     8      |   5
   2    |     1      |   3
   2    |     5      |   5
   ...
```

### Bước 2: Thuật toán ALS (Alternating Least Squares)

**ALS hoạt động như thế nào?**

Mục tiêu: Phân rã ma trận rating thành 2 ma trận nhỏ hơn chứa các "đặc trưng ẩn"

```
Ma trận Rating (User × Product)
┌─────────────────────────────┐
│  U1  U2  U3  U4  U5         │
│ ┌───┬───┬───┬───┬───┐       │
│ │ 4 │ 3 │ 5 │ 5 │ 5 │ P1    │
│ ├───┼───┼───┼───┼───┤       │
│ │ 5 │ ? │ 5 │ 5 │ 4 │ P2    │
│ ├───┼───┼───┼───┼───┤       │
│ │ 4 │ 4 │ 4 │ ? │ 3 │ P3    │
│ └───┴───┴───┴───┴───┘       │
└─────────────────────────────┘
         ⬇ ALS ⬇
┌──────────────────┐   ┌──────────────────┐
│ Ma trận User     │ × │ Ma trận Product  │
│ (Users × Factors)│   │ (Factors × Prods)│
│                  │   │                  │
│ U1 [0.8, 0.2, …] │   │ [0.5] P1         │
│ U2 [0.3, 0.9, …] │   │ [0.7] P2         │
│ U3 [0.6, 0.4, …] │   │ [0.3] P3         │
│ U4 [0.9, 0.1, …] │   │  …               │
│ U5 [0.7, 0.5, …] │   │                  │
└──────────────────┘   └──────────────────┘
   (10 factors)           (10 factors)
```

**Ý nghĩa các "factors" (đặc trưng ẩn):**
- Mỗi factor đại diện cho một đặc điểm ẩn (ví dụ: "tech-savvy", "giá rẻ", "chất lượng cao"...)
- User có vector factors → thể hiện sở thích của user
- Product có vector factors → thể hiện đặc tính của product

### Bước 3: Dự đoán điểm số

**Công thức:**
```
Điểm dự đoán = User_Vector · Product_Vector
             = (tích vô hướng của 2 vector)
```

**Ví dụ cụ thể:**
```
User 1 có vector: [0.8, 0.3, 0.5, 0.2, 0.7, 0.4, 0.6, 0.1, 0.9, 0.3]
Product 2 có vector: [0.7, 0.5, 0.4, 0.3, 0.8, 0.2, 0.5, 0.6, 0.7, 0.4]

Điểm dự đoán = 0.8×0.7 + 0.3×0.5 + 0.5×0.4 + ... 
             ≈ 4.97 (rất phù hợp!)
```

### Bước 4: Tạo gợi ý Top-K

Với mỗi user, tính điểm cho TẤT CẢ sản phẩm (kể cả chưa mua), rồi chọn Top-K cao nhất:

```
User 1:
  Product 2  → 4.97 ⭐ (Top 1)
  Product 10 → 4.92 ⭐ (Top 2)
  Product 8  → 4.68 ⭐ (Top 3)
  Product 7  → 4.39 ⭐ (Top 4)
  ...
```

**Kết quả xuất ra `artifacts/recommendations/user_recs/`:**
```csv
user_id,product_id,score
1,2,4.972
1,10,4.9174
1,8,4.6807
1,7,4.3899
```

---

## PHẦN 2: GỢI Ý SẢN PHẨM TƯƠNG TỰ (Item Similarity)

### Bước 1: Lấy vector đặc trưng sản phẩm

Từ mô hình ALS, mỗi sản phẩm có 1 vector 10 chiều:
```
Product 1: [0.5, 0.7, 0.3, 0.9, 0.2, 0.4, 0.8, 0.1, 0.6, 0.3]
Product 2: [0.4, 0.8, 0.2, 0.9, 0.3, 0.3, 0.7, 0.2, 0.5, 0.4]
Product 3: [0.9, 0.1, 0.8, 0.2, 0.7, 0.6, 0.3, 0.4, 0.2, 0.5]
...
```

### Bước 2: Chuẩn hóa vector (Normalization)

Để tính cosine similarity, ta cần chuẩn hóa mỗi vector về độ dài = 1:

```
Vector gốc: [3, 4]
Độ dài (norm): √(3² + 4²) = √25 = 5
Vector chuẩn hóa: [3/5, 4/5] = [0.6, 0.8]
```

**Code Spark:**
```python
norm = sqrt(sum(x²))  # Tính độ dài vector
features_norm = features / norm  # Chia mỗi phần tử cho độ dài
```

### Bước 3: Tính Cosine Similarity

**Công thức:**
```
Cosine Similarity = A · B / (||A|| × ||B||)
                  = A_norm · B_norm  (nếu đã chuẩn hóa)
```

**Ý nghĩa hình học:**
```
    B
    ↗
   /  θ (góc)
  /
 /________→ A

cos(θ) = độ tương đồng
  = 1.0: giống hệt nhau (θ = 0°)
  = 0.0: không liên quan (θ = 90°)
  = -1.0: đối lập (θ = 180°)
```

**Ví dụ tính toán:**
```
Product 3 vector chuẩn hóa: [0.6, 0.3, 0.5, 0.4, 0.2, 0.7, 0.1, 0.6, 0.3, 0.5]
Product 7 vector chuẩn hóa: [0.5, 0.4, 0.6, 0.3, 0.2, 0.8, 0.1, 0.5, 0.4, 0.4]

Cosine = 0.6×0.5 + 0.3×0.4 + 0.5×0.6 + ... 
       = 0.9623 (rất giống nhau!)
```

### Bước 4: Tạo ma trận tương đồng

So sánh TẤT CẢ cặp sản phẩm (cross join):
```
Product 3 vs:
  Product 7  → 0.9623 ⭐ (Top 1)
  Product 8  → 0.9315 ⭐ (Top 2)
  Product 10 → 0.8960 ⭐ (Top 3)
  Product 1  → 0.8188 ⭐ (Top 4)
  ...
```

**Kết quả xuất ra `artifacts/recommendations/item_similarities/`:**
```csv
source_product_id,similar_product_id,similarity
3,7,0.9623
3,8,0.9315
3,10,0.896
3,1,0.8188
```

---

## PHẦN 3: HIỂN THỊ TRÊN STREAMLIT

### Tab "Gợi ý cho người dùng"
1. User chọn `user_id` = 1
2. Streamlit đọc file `user_recs.csv`, lọc dòng có `user_id = 1`
3. Hiển thị Top-K sản phẩm với điểm cao nhất
4. Vẽ biểu đồ cột thể hiện điểm dự đoán

**Ý nghĩa:**
- Điểm cao → Sản phẩm phù hợp với sở thích user
- Dựa trên lịch sử rating của user và những user tương tự

### Tab "Sản phẩm tương tự"
1. User chọn `product_id` = 3
2. Streamlit đọc file `item_similarities.csv`, lọc `source_product_id = 3`
3. Hiển thị Top-K sản phẩm có độ tương đồng cao nhất
4. Vẽ biểu đồ thể hiện điểm similarity

**Ý nghĩa:**
- Similarity cao → Sản phẩm có đặc tính giống nhau
- Hữu ích cho "Khách hàng xem sản phẩm này cũng xem..."

---

## TẠI SAO CÁCH NÀY HIỆU QUẢ?

### 1. **ALS xử lý được Big Data**
- Spark phân tán tính toán trên nhiều node
- Không cần load toàn bộ ma trận vào RAM
- Scale tốt cho hàng triệu user/product

### 2. **Xử lý "cold start" và missing data**
- Ma trận rating thưa (nhiều ô trống)
- ALS học được pattern ẩn để dự đoán ô trống
- ColdStartStrategy="drop" bỏ qua user/product mới (chưa có data)

### 3. **Item similarity bổ sung**
- Gợi ý dựa trên nội dung sản phẩm (content-based)
- Không phụ thuộc vào user khác
- Tốt cho sản phẩm mới (có đặc trưng nhưng ít rating)

### 4. **Kết hợp 2 phương pháp (Hybrid)**
- User-based: "Người giống bạn thích gì?"
- Item-based: "Sản phẩm này giống cái gì?"
- Cho kết quả toàn diện hơn

---

## VÍ DỤ THỰC TẾ TRONG PROJECT

### Ví dụ 1: User 1 thích công nghệ
```
Lịch sử rating của User 1:
  Mechanical Keyboard (Electronics) → 4★
  Noise Cancelling Headphones → 5★
  Data Science Book → 5★
  
Hệ thống học được: User 1 có xu hướng thích tech và học tập

Gợi ý cho User 1:
  1. Noise Cancelling Headphones (4.97★) - chưa mua nhưng giống sở thích
  2. Mechanical Keyboard (4.92★)
  3. Data Science Book (4.68★)
  4. Slim Fit Jeans (4.39★) - điểm thấp hơn vì khác sở thích
```

### Ví dụ 2: Sản phẩm tương tự với Product 3 (Data Science Book)
```
Product 3: Data Science Book (Books, $35)

Sản phẩm tương tự:
  1. Slim Fit Jeans (0.9623) - Cùng tầm giá, được user tương tự mua
  2. Data Science Book (0.9315) - Cùng danh mục
  3. Noise Cancelling Headphones (0.896) - User thích tech thường mua cả 2
  4. Wireless Mouse (0.8188) - Accessory cho tech user
```

---

## TÓM TẮT FLOW HOÀN CHỈNH

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. Thu thập dữ liệu                          │
│  User đánh giá sản phẩm → Lưu vào ratings.csv                   │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│               2. Huấn luyện mô hình (Spark Job)                 │
│  • Đọc ratings.csv                                              │
│  • Chạy ALS algorithm → Học user/product vectors                │
│  • Tính toán gợi ý Top-K cho mỗi user                           │
│  • Tính toán similarity giữa các sản phẩm                       │
│  • Xuất kết quả → artifacts/                                    │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│               3. Hiển thị trên Streamlit                        │
│  • Đọc artifacts/recommendations/                               │
│  • User chọn user_id hoặc product_id                            │
│  • Hiển thị gợi ý + biểu đồ                                     │
│  • Cập nhật real-time khi có data mới                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## CÂU HỎI THƯỜNG GẶP

**Q1: Tại sao điểm dự đoán không phải từ 1-5 như rating gốc?**
A: ALS dự đoán dựa trên tích vô hướng của vectors, không bị giới hạn. Nhưng thường các sản phẩm được gợi ý sẽ có điểm trong khoảng hợp lý.

**Q2: Làm sao biết mô hình tốt?**
A: Đánh giá bằng RMSE (Root Mean Square Error) trên test set. Điểm RMSE càng thấp càng tốt.

**Q3: Điều gì xảy ra nếu có user mới (chưa rating gì)?**
A: Cold start problem - có thể dùng:
  - Item-based recommendation (gợi ý sản phẩm hot)
  - Hỏi user sở thích ban đầu
  - Hybrid với content-based filtering

**Q4: Similarity = 1.0 có nghĩa gì?**
A: 2 sản phẩm có vector đặc trưng giống hệt nhau (có thể trùng lặp dữ liệu hoặc rất giống nhau về pattern người mua).

**Q5: Tại sao dùng cosine chứ không dùng Euclidean distance?**
A: Cosine đo góc (hướng), không bị ảnh hưởng bởi độ lớn. Tốt hơn cho recommendation vì ta quan tâm pattern, không phải giá trị tuyệt đối.

---

## KẾT LUẬN

Hệ thống gợi ý này sử dụng:
- **Machine Learning** (ALS) để học pattern từ dữ liệu
- **Linear Algebra** (vector, cosine) để tính toán tương đồng
- **Big Data Processing** (Spark) để xử lý quy mô lớn
- **Visualization** (Streamlit) để người dùng tương tác

Đây là một giải pháp hoàn chỉnh, production-ready cho hệ thống e-commerce!
