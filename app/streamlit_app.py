import os
from pathlib import Path
import glob

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"

st.set_page_config(page_title="Phân tích & Gợi ý sản phẩm", layout="wide")
sns.set_theme(style="whitegrid", context="paper")

# Compact plotting helpers
PRIMARY_COLOR = "#4C78A8"

# Sidebar size control
st.sidebar.markdown("### Tuỳ chỉnh hiển thị")
chart_scale = st.sidebar.slider("Tỉ lệ kích thước biểu đồ", min_value=0.6, max_value=1.2, value=0.8, step=0.1)

def small_fig(w=4.0, h=2.4):
    return plt.subplots(figsize=(w * chart_scale, h * chart_scale))


def find_single_csv(dir_path: Path) -> Path | None:
    if not dir_path.exists():
        return None
    # Spark writes part-*.csv files inside a directory
    parts = sorted(dir_path.glob("part-*.csv"))
    if parts:
        return parts[0]
    # fallback: any csv inside
    any_csv = sorted(dir_path.glob("*.csv"))
    return any_csv[0] if any_csv else None


def load_csv_dir(rel_dir: str) -> pd.DataFrame | None:
    target_dir = ARTIFACTS / rel_dir
    part = find_single_csv(target_dir)
    if part and part.exists():
        return pd.read_csv(part)
    return None


st.title("Bảng điều khiển phân tích & gợi ý sản phẩm")
st.caption("PySpark + Pandas + Seaborn/Matplotlib + Streamlit")

# Sidebar controls
st.sidebar.header("Điều khiển")
reload_clicked = st.sidebar.button("Tải lại dữ liệu")

# Load datasets
rating_dist = load_csv_dir("aggregates/rating_distribution")
cat_counts = load_csv_dir("aggregates/category_counts")
top_products = load_csv_dir("aggregates/top_products")
user_activity = load_csv_dir("aggregates/user_activity")
user_recs = load_csv_dir("recommendations/user_recs")
item_sims = load_csv_dir("recommendations/item_similarities")
clusters = load_csv_dir("clusters/product_clusters")

# Tabs
overview_tab, recs_tab, clusters_tab = st.tabs(["Tổng quan", "Gợi ý", "Cụm sản phẩm"]) 

with overview_tab:
    st.subheader("Phân phối điểm đánh giá")
    if rating_dist is not None:
        fig, ax = small_fig(5, 3)
        sns.barplot(data=rating_dist, x="rating", y="count", ax=ax, color=PRIMARY_COLOR)
        ax.set_xlabel("Điểm đánh giá")
        ax.set_ylabel("Số lượng")
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        st.pyplot(fig, use_container_width=False, clear_figure=True)
    else:
        st.info("No rating_distribution found. Run the ETL job first.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sản phẩm nổi bật (theo số đánh giá)")
        if top_products is not None:
            top_view = top_products.head(8).copy()
            fig, ax = small_fig(5, 4)
            sns.barplot(data=top_view, y="name", x="rating_count", ax=ax, color=PRIMARY_COLOR)
            ax.set_ylabel("Sản phẩm")
            ax.set_xlabel("Số lượng đánh giá")
            st.pyplot(fig, use_container_width=False, clear_figure=True)
        else:
            st.info("No top_products found.")

    with col2:
        st.subheader("Mức độ tương tác theo danh mục")
        if cat_counts is not None:
            fig, ax = small_fig(5, 4)
            sns.barplot(data=cat_counts, x="category", y="count", ax=ax, color=PRIMARY_COLOR)
            ax.set_xlabel("Danh mục")
            ax.set_ylabel("Số lượng đánh giá")
            ax.tick_params(axis='x', rotation=30)
            st.pyplot(fig, use_container_width=False, clear_figure=True)
        else:
            st.info("No category_counts found.")

with recs_tab:
    st.subheader("Gợi ý")
    left, right = st.columns(2)

    with left:
        st.markdown("#### Gợi ý theo người dùng")
        if user_recs is None:
            st.info("No user recommendations found. Run the ALS recommender job.")
        else:
            users = sorted(user_recs["user_id"].unique().tolist())
            selected_user = st.selectbox("Chọn người dùng (user_id)", options=users, key="sel_user")
            k_user = st.slider("Số lượng gợi ý (Top-K)", min_value=3, max_value=20, value=10, key="k_user")

            recs = user_recs[user_recs["user_id"] == selected_user].nlargest(k_user, "score")
            product_names = None
            if clusters is not None:
                product_names = clusters[["product_id", "name", "category", "price"]].drop_duplicates()
            if product_names is not None:
                recs = recs.merge(product_names, on="product_id", how="left")
            # Đổi tên cột hiển thị cho thân thiện
            display_recs = recs.rename(columns={
                "user_id": "Người dùng",
                "product_id": "Sản phẩm",
                "score": "Điểm dự đoán",
                "name": "Tên",
                "category": "Danh mục",
                "price": "Giá"
            })
            st.dataframe(display_recs.reset_index(drop=True))
            if not recs.empty:
                fig, ax = small_fig(4.8, 2.6)
                sns.barplot(data=recs, y="product_id", x="score", ax=ax, color=PRIMARY_COLOR)
                ax.set_ylabel("Mã sản phẩm")
                ax.set_xlabel("Điểm dự đoán")
                ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.2f}"))
                st.pyplot(fig, use_container_width=False, clear_figure=True)

    with right:
        st.markdown("#### Sản phẩm tương tự (item-item)")
        if item_sims is None:
            st.info("No item similarities found. Re-run the recommender job.")
        else:
            items = sorted(set(item_sims["source_product_id"].unique().tolist()))
            sel_item = st.selectbox("Chọn sản phẩm (product_id)", options=items, key="sel_item")
            k_item = st.slider("Số lượng tương tự (Top-K)", min_value=3, max_value=20, value=10, key="k_item")
            sims = (
                item_sims[item_sims["source_product_id"] == sel_item]
                .nlargest(k_item, "similarity")
                .rename(columns={"similar_product_id": "product_id"})
            )
            if clusters is not None:
                names = clusters[["product_id", "name", "category", "price"]].drop_duplicates()
                sims = sims.merge(names, on="product_id", how="left")
            display_sims = sims.rename(columns={
                "similarity": "Độ tương đồng",
                "product_id": "Sản phẩm",
                "name": "Tên",
                "category": "Danh mục",
                "price": "Giá"
            })
            st.dataframe(display_sims.reset_index(drop=True))
            if not sims.empty:
                fig, ax = small_fig(4.8, 2.6)
                sns.barplot(data=sims, y="product_id", x="similarity", ax=ax, color=PRIMARY_COLOR)
                ax.set_ylabel("Mã sản phẩm")
                ax.set_xlabel("Độ tương đồng (cosine)")
                ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.2f}"))
                st.pyplot(fig, use_container_width=False, clear_figure=True)

with clusters_tab:
    st.subheader("Cụm sản phẩm")
    if clusters is None:
        st.info("No clusters found. Run the clustering job.")
    else:
        cluster_ids = sorted(clusters["cluster"].unique().tolist())
        selected_cluster = st.selectbox("Chọn cụm", options=cluster_ids)
        view = clusters[clusters["cluster"] == selected_cluster].copy()
        st.write(f"Sản phẩm trong cụm {selected_cluster}:")
        df_display = view[["product_id", "name", "category", "price", "avg_rating", "rating_count"]].rename(columns={
            "product_id": "Sản phẩm",
            "name": "Tên",
            "category": "Danh mục",
            "price": "Giá",
            "avg_rating": "Điểm TB",
            "rating_count": "Số đánh giá"
        })
        st.dataframe(df_display.reset_index(drop=True))

st.divider()
st.caption("Mẹo: Nếu chưa thấy dữ liệu, hãy chạy các job Spark để tạo dữ liệu trong thư mục artifacts trước.")
