from utils.config import make_spark, input_path, output_path
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans


def main():
    spark = make_spark("Product-Clustering")

    products = (
        spark.read.option("header", True).option("inferSchema", True).csv(input_path("products.csv"))
    )
    ratings = (
        spark.read.option("header", True).option("inferSchema", True).csv(input_path("ratings.csv"))
    )

    stats = (
        ratings.groupBy("product_id")
        .agg(F.count("*").alias("rating_count"), F.avg("rating").alias("avg_rating"))
    )

    df = (
        products.join(stats, on="product_id", how="left")
        .fillna({"rating_count": 0, "avg_rating": 0.0})
        .withColumn("price", F.col("price").cast("double"))
    )

    # Feature engineering: category (one-hot), price, avg_rating, rating_count
    cat_indexer = StringIndexer(inputCol="category", outputCol="category_idx", handleInvalid="keep")
    cat_ohe = OneHotEncoder(inputCol="category_idx", outputCol="category_ohe")

    assembler = VectorAssembler(
        inputCols=["category_ohe", "price", "avg_rating", "rating_count"],
        outputCol="features_raw",
    )

    scaler = StandardScaler(inputCol="features_raw", outputCol="features", withStd=True, withMean=False)

    kmeans = KMeans(k=4, seed=42, featuresCol="features", predictionCol="cluster")

    pipeline = Pipeline(stages=[cat_indexer, cat_ohe, assembler, scaler, kmeans])
    model = pipeline.fit(df)

    result = model.transform(df)

    out = result.select("product_id", "name", "category", "price", "avg_rating", "rating_count", "cluster")

    out.coalesce(1).write.mode("overwrite").option("header", True).csv(
        output_path("clusters/product_clusters")
    )

    print("Clustering completed. Outputs written to artifacts/clusters.")


if __name__ == "__main__":
    main()
