from utils.config import make_spark, input_path, output_path
from pyspark.sql import functions as F


def main():
    spark = make_spark("ETL-Prepare-Data")

    products = (
        spark.read.option("header", True).option("inferSchema", True).csv(input_path("products.csv"))
    )
    ratings = (
        spark.read.option("header", True).option("inferSchema", True).csv(input_path("ratings.csv"))
    )

    # rating stats per product
    prod_stats = (
        ratings.groupBy("product_id")
        .agg(
            F.count("rating").alias("rating_count"),
            F.avg("rating").alias("avg_rating"),
        )
        .join(products, on="product_id", how="left")
    )

    top_products = prod_stats.orderBy(F.desc("rating_count"), F.desc("avg_rating"))
    top_products.coalesce(1).write.mode("overwrite").option("header", True).csv(
        output_path("aggregates/top_products")
    )

    # rating distribution
    rating_dist = ratings.groupBy("rating").agg(F.count("*").alias("count")).orderBy("rating")
    rating_dist.coalesce(1).write.mode("overwrite").option("header", True).csv(
        output_path("aggregates/rating_distribution")
    )

    # category counts (by number of ratings)
    cat_counts = (
        ratings.join(products.select("product_id", "category"), on="product_id", how="left")
        .groupBy("category")
        .agg(F.count("*").alias("count"))
        .orderBy(F.desc("count"))
    )
    cat_counts.coalesce(1).write.mode("overwrite").option("header", True).csv(
        output_path("aggregates/category_counts")
    )

    # user activity
    user_activity = ratings.groupBy("user_id").agg(F.count("*").alias("ratings_made"))
    user_activity.coalesce(1).write.mode("overwrite").option("header", True).csv(
        output_path("aggregates/user_activity")
    )

    print("ETL completed. Outputs written to artifacts/aggregates (or HDFS equivalent).")


if __name__ == "__main__":
    main()
