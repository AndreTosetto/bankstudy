# Databricks notebook source
# MAGIC %md
# MAGIC import sql functions

# COMMAND ----------

from pyspark.sql import *
from pyspark.sql.functions import when, desc, asc
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

# COMMAND ----------

# MAGIC %md
# MAGIC Connection

# COMMAND ----------

spark.conf.set("fs.azure.account.key..dfs.core.windows.net",
                "<KEY>")

# COMMAND ----------

dfClienteSRC = spark.read.csv("abfss://bronze@saneobankpocunit.dfs.core.windows.net/NeoBank_Modelling_Source.csv", header=True)
dfClienteTAG = spark.read.csv("abfss://gold@saneobankpocunit.dfs.core.windows.net/NeoBank_Modelling.csv", header=True)

# COMMAND ----------

display (dfClienteSRC)
display (dfClienteTAG)

# COMMAND ----------

# DBTITLE 1,Filter Active Members
dfClienteSRC = dfClienteSRC.filter(dfClienteSRC.IsActiveMember == 1)

# COMMAND ----------

# DBTITLE 1,Renaming Columns
dfClienteSRC = dfClienteSRC.withColumnRenamed("RowNumber", "RowNumber_SRC")\
                .withColumnRenamed("CustomerId", "CustomerId_SRC")\
                .withColumnRenamed("Surname", "Surname_SRC")\
                .withColumnRenamed("CreditScore", "CreditScore_SRC")\
                .withColumnRenamed("Geography", "Geography_SRC")\
                .withColumnRenamed("Gender", "Gender_SRC")\
                .withColumnRenamed("Age", "Age_SRC")\
                .withColumnRenamed("Tenure", "Tenure_SRC")\
                .withColumnRenamed("Balance", "Balance_SRC")\
                .withColumnRenamed("NumOfProducts", "NumOfProducts_SRC")\
                .withColumnRenamed("HasCrCard", "HasCrCard_SRC")\
                .withColumnRenamed("IsActiveMember", "IsActiveMember_SRC")\
                .withColumnRenamed("EstimatedSalary", "EstimatedSalary_SRC")\
                .withColumnRenamed("Exited", "Exited_SRC")

dfClienteTAG = dfClienteTAG.withColumnRenamed("RowNumber", "RowNumber_TAG")\
                .withColumnRenamed("CustomerId", "CustomerId_TAG")\
                .withColumnRenamed("Surname", "Surname_TAG")\
                .withColumnRenamed("CreditScore", "CreditScore_TAG")\
                .withColumnRenamed("Geography", "Geography_TAG")\
                .withColumnRenamed("Gender", "Gender_TAG")\
                .withColumnRenamed("Age", "Age_TAG")\
                .withColumnRenamed("Tenure", "Tenure_TAG")\
                .withColumnRenamed("Balance", "Balance_TAG")\
                .withColumnRenamed("NumOfProducts", "NumOfProducts_TAG")\
                .withColumnRenamed("HasCrCard", "HasCrCard_TAG")\
                .withColumnRenamed("IsActiveMember", "IsActiveMember_TAG")\
                .withColumnRenamed("EstimatedSalary", "EstimatedSalary_TAG")\
                .withColumnRenamed("Exited", "Exited_TAG")

dfClienteSRC.show()
dfClienteTAG.show()

# COMMAND ----------

# DBTITLE 1,Joins to check the registers on the destination table
dfClientJoin = dfClienteSRC.join(dfClienteTAG, dfClienteSRC.CustomerId_SRC == dfClienteTAG.CustomerId_TAG, "left")
display(dfClientJoin)

# COMMAND ----------

# DBTITLE 1,New Clients
dfNewRegister = dfClientJoin.where('CustomerId_TAG is null')

#Selecionar Colunas
dfNewRegister = dfNewRegister.select('RowNumber_SRC', 'CustomerId_SRC', 'Surname_SRC', 'CreditScore_SRC',
                                      'Geography_SRC', 'Gender_SRC', 'Age_SRC', 'Tenure_SRC', 'Balance_SRC', 'NumOfProducts_SRC',
                                       'HasCrCard_SRC', 'IsActiveMember_SRC', 'EstimatedSalary_SRC', 'Exited_SRC')

display(dfNewRegister)

# COMMAND ----------

# DBTITLE 1,Update Clients
dfUpdate = dfClientJoin.where((dfClientJoin.CustomerId_TAG == dfClientJoin.CustomerId_SRC) & 
                              ((dfClientJoin.Surname_SRC != dfClientJoin.Surname_TAG) |
                               (dfClientJoin.CreditScore_SRC != dfClientJoin.CreditScore_TAG) |
                               (dfClientJoin.Geography_SRC != dfClientJoin.Geography_TAG) |
                               (dfClientJoin.Gender_SRC != dfClientJoin.Gender_TAG) |
                               (dfClientJoin.Age_SRC != dfClientJoin.Age_TAG) |
                               (dfClientJoin.Tenure_SRC != dfClientJoin.Tenure_TAG) |
                               (dfClientJoin.Balance_SRC != dfClientJoin.Balance_TAG) |
                               (dfClientJoin.NumOfProducts_SRC != dfClientJoin.NumOfProducts_TAG) |
                               (dfClientJoin.HasCrCard_SRC != dfClientJoin.HasCrCard_TAG) |
                               (dfClientJoin.IsActiveMember_SRC != dfClientJoin.IsActiveMember_TAG) |
                               (dfClientJoin.EstimatedSalary_SRC != dfClientJoin.EstimatedSalary_TAG) |
                               (dfClientJoin.Exited_SRC != dfClientJoin.Exited_TAG)))

dfUpdateInativos = dfUpdate

#Selecionar o dataframe de updates Ativos
dfUpdate = dfUpdate.select('RowNumber_SRC', 'CustomerId_SRC', 'Surname_SRC', 'CreditScore_SRC',
                           'Geography_SRC', 'Gender_SRC', 'Age_SRC', 'Tenure_SRC', 'Balance_SRC', 
                           'NumOfProducts_SRC', 'HasCrCard_SRC', 'IsActiveMember_SRC', 'EstimatedSalary_SRC', 'Exited_SRC')
                    
#Selecionar o dataframe de updates Inativos
dfUpdateInativos = dfUpdateInativos.select('RowNumber_TAG', 'CustomerId_TAG', 'Surname_TAG', 'CreditScore_TAG',
                                           'Geography_TAG', 'Gender_TAG', 'Age_TAG', 'Tenure_TAG', 'Balance_TAG', 
                                           'NumOfProducts_TAG', 'HasCrCard_TAG', 'IsActiveMember_TAG', 'EstimatedSalary_TAG', 'Exited_TAG')

display(dfUpdate)
display(dfUpdateInativos)

# COMMAND ----------

# DBTITLE 1,Deactivate Register Process
dfUpdateInativos = dfUpdateInativos.select('*').withColumn('IsActiveMember_TAG', when(dfUpdateInativos.IsActiveMember_TAG == '1', '0')\
                                                            .otherwise(dfUpdateInativos.IsActiveMember_TAG))

# COMMAND ----------

display(dfNewRegister)
display(dfUpdate)
display(dfUpdateInativos)

# COMMAND ----------

# DBTITLE 1,Inativar o Registro
dfMerge = dfClienteTAG.unionAll(dfUpdateInativos)


# COMMAND ----------

display(dfMerge.where('CustomerId_TAG == 15628319'))
dfMerge.count()

# COMMAND ----------

dfMerge = dfMerge.withColumn('_row_number', row_number().over(Window.partitionBy('CustomerId_TAG').orderBy('IsActiveMember_TAG')))

# COMMAND ----------

dfMerge = dfMerge.select('*').where('_row_number == 1')
display(dfMerge.where('CustomerId_TAG == 15628319'))

# COMMAND ----------

# DBTITLE 1,Drop _row_number Column
dfMerge = dfMerge.drop('_row_number')

# COMMAND ----------

# DBTITLE 1,Acrescentar registros e updates
dfVersionFinal = dfMerge.unionAll(dfNewRegister).unionAll(dfUpdate)

# COMMAND ----------

display(dfVersionFinal)

display(dfVersionFinal.select('*').where('CustomerId_TAG == 15628319 or CustomerId_TAG == 215628319'))

dfVersionFinal.count()

# COMMAND ----------

# DBTITLE 1,Load in  Container Silver
dfVersionFinal = dfVersionFinal.withColumnRenamed("RowNumber_TAG", "RowNumber")\
                .withColumnRenamed("CustomerId_TAG", "CustomerId")\
                .withColumnRenamed("Surname_TAG", "Surname")\
                .withColumnRenamed("CreditScore_TAG", "CreditScore")\
                .withColumnRenamed("Geography_TAG", "Geography")\
                .withColumnRenamed("Gender_TAG", "Gender")\
                .withColumnRenamed("Age_TAG", "Age")\
                .withColumnRenamed("Tenure_TAG", "Tenure")\
                .withColumnRenamed("Balance_TAG", "Balance")\
                .withColumnRenamed("NumOfProducts_TAG", "NumOfProducts")\
                .withColumnRenamed("HasCrCard_TAG", "HasCrCard")\
                .withColumnRenamed("IsActiveMember_TAG", "IsActiveMember")\
                .withColumnRenamed("EstimatedSalary_TAG", "EstimatedSalary")\
                .withColumnRenamed("Exited_TAG", "Exited")

#display(dfVersionFinal)

dfVersionFinal.coalesce(1).write.mode("overwrite").csv(path="abfss://silver@saneobankpocunit.dfs.core.windows.net/NeoBank_Modelling", header=True)
