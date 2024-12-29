# Databricks notebook source
client_id = 'client_id'
tenant_id = 'tenant_id'
client_secret = 'client_secret'

storage_account_name = 'storage_account_name'
container_name  = 'container_name'


# COMMAND ----------

configs = {
  "fs.azure.account.auth.type": "OAuth",
  "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
  "fs.azure.account.oauth2.client.id": client_id,
  "fs.azure.account.oauth2.client.secret": client_secret,
  "fs.azure.account.oauth2.client.endpoint": f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
}


# COMMAND ----------

dbutils.fs.mount(
  source = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/",
  mount_point = f"/mnt/saneobankpocunit/bronze",
  extra_configs = configs
)

# COMMAND ----------

display(dbutils.fs.mounts())

# COMMAND ----------

display(dbutils.fs.ls('mnt/saneobankpocunit/bronze'))

# COMMAND ----------

df = spark.read.csv('dbfs:/mnt/saneobankpocunit/bronze/NeoBank_Modelling.csv', header=True)

# COMMAND ----------


