# Databricks notebook source
# MAGIC %md
# MAGIC Connection Key

# COMMAND ----------

spark.conf.set("fs.azure.account.key..dfs.core.windows.net",
                "")

# COMMAND ----------

df = spark.read.csv("abfss://bronze@saneobankpocunit.dfs.core.windows.net/NeoBank_Modelling.csv", header=True)

# COMMAND ----------

display(df)

