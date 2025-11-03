from utils.config import make_spark, input_path, output_path
from pyspark.sql import functions as F
from pyspark.sql import Window
from pyspark.ml.recommendation import ALS


def main():
    spark = make_spark("ALS-Recommender")

    ratings = (
        spark.read.option("header", True).option("inferSchema", True).csv(input_path("ratings.csv"))
        .select(F.col("user_id").cast("int"), F.col("product_id").cast("int"), F.col("rating").cast("float"))
        .na.drop()
    )

    # Basic ALS config (tune as needed)
    als = ALS(
        userCol="user_id",
        itemCol="product_id",
        ratingCol="rating",
        nonnegative=True,
        coldStartStrategy="drop",
        rank=10,
        maxIter=10,
        regParam=0.1,
    )

    model = als.fit(ratings)

    # Top-N per user
    user_recs = model.recommendForAllUsers(10)
    user_recs_flat = (
        user_recs.select(
            "user_id",
            F.explode("recommendations").alias("rec"),
        )
        .select(F.col("user_id"), F.col("rec.product_id").alias("product_id"), F.col("rec.rating").alias("score"))
    )
    user_recs_flat.coalesce(1).write.mode("overwrite").option("header", True).csv(
        output_path("recommendations/user_recs")
    )

    # Item-item similarity via cosine on item factors (pure Spark SQL, no Python UDF)
    # NOTE: O(n^2) cross join — OK for demo/small catalogs. Use ANN for large scale.
    item_factors = model.itemFactors.select(F.col("id").alias("product_id"), F.col("features"))
    item_factors = item_factors.withColumn(
        "norm",
        F.expr("sqrt(aggregate(features, cast(0.0 as double), (acc, x) -> acc + x*x))"),
    ).withColumn(
        "features_norm",
        F.expr("transform(features, x -> IF(norm > 0, x / norm, 0.0))"),
    )

    pairs = (
        item_factors.alias("i")
        .crossJoin(item_factors.alias("j"))
        .where(F.col("i.product_id") != F.col("j.product_id"))
    )

    sims = pairs.select(
        F.col("i.product_id").alias("source_product_id"),
        F.col("j.product_id").alias("similar_product_id"),
        F.expr(
            "aggregate(zip_with(i.features_norm, j.features_norm, (x, y) -> x * y), cast(0.0 as double), (acc, x) -> acc + x)"
        ).alias("similarity"),
    )

    w = Window.partitionBy("source_product_id").orderBy(F.desc("similarity"))
    top_sim = sims.withColumn("rk", F.row_number().over(w)).where(F.col("rk") <= 10).drop("rk")

    top_sim.coalesce(1).write.mode("overwrite").option("header", True).csv(
        output_path("recommendations/item_similarities")
    )

    print("Recommender completed. Outputs written to artifacts/recommendations.")


if __name__ == "__main__":
    main()
