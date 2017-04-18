package edu.gatech.cs6250.main

import com.databricks.spark.csv.CsvContext
import org.apache.spark.sql.SQLContext
import org.apache.spark.{SparkConf, SparkContext}

/**
  * Created by chanes on 4/7/17.
  */
object Main {
  def main(args: Array[String]) {

    val sc = createContext
    val sqlContext = new SQLContext(sc)

    val notes_df = sqlContext.csvFile("data/NOTEEVENTS.csv")
    notes_df.registerTempTable("note_events")
    println(notes_df.show(10))
  }

  def createContext(appName: String, masterUrl: String): SparkContext = {
    val conf = new SparkConf().setAppName(appName).setMaster(masterUrl)
    new SparkContext(conf)
  }

  def createContext(appName: String): SparkContext = createContext(appName, "local")

  def createContext: SparkContext = createContext("cs6250 project", "local")
}
