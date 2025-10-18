import better.files._
import io.shiftleft.semanticcpg.language._
import java.io.{File, PrintWriter, FileWriter, BufferedWriter}
import java.nio.file.{Files, Paths}

@main def generateCfgFromSingleFile(inputFilePath: String, outputPath: String, methodName: String) = {
  
  val inputFile = new File(inputFilePath)
  
  // Validate input file
  if (!inputFile.exists()) {
    println(s"Error: Input file does not exist: $inputFilePath")
    //return ()
  }
  
  if (!inputFile.getName.endsWith(".java")) {
    println(s"Error: Input file must be a .java file: $inputFilePath")
    // return ()
  }
  
  val fileName = inputFile.getName
  
  // Create output directory if it doesn't exist
  val outputFile = new File(outputPath)
  val outputDir = outputFile.getParentFile
  if (outputDir != null && !outputDir.exists()) {
    outputDir.mkdirs()
  }
  

  
  try {
    println(s"Processing: $fileName")
    
    
    println(s"Looking for method: $methodName")
    
    // Try multiple import approaches
    var importSucceeded = false
    
    // Approach 1: Standard import
    try {
      importCode.java(inputFilePath)
      importSucceeded = true
      println("✓ Standard import succeeded")
    } catch {
      case e: Exception => 
        println(s"Standard import failed: ${e.getMessage}")
    }
    
    // Approach 2: Absolute path
    if (!importSucceeded) {
      try {
        importCode(inputFile.getAbsolutePath)
        importSucceeded = true
        println("✓ Absolute path import succeeded")
      } catch {
        case e: Exception => 
          println(s"Absolute path import failed: ${e.getMessage}")
      }
    }
    
    // Approach 3: From string content
    if (!importSucceeded) {
      try {
        val fileContent = scala.io.Source.fromFile(inputFilePath).mkString
        importCode.java.fromString(fileContent)
        importSucceeded = true
        println("✓ String content import succeeded")
      } catch {
        case e: Exception => 
          println(s"String content import failed: ${e.getMessage}")
        
          
          throw new Exception(s"Unable to import file: ${e.getMessage}")
      }
    }
    
    if (importSucceeded) {
               // Check if method exists
      if (cpg.method.name(methodName).size > 0) {
        val outputFile = s"$outputPath/cfg/Sample.java.dot"
  //Generate CFG graph
        val dotCfg = cpg.method(methodName).dotCfg
            if (dotCfg.nonEmpty) {
                val file = new java.io.File(outputFile)
                val writer = new java.io.PrintWriter(file)
                writer.write(dotCfg.head)
                writer.close()
                println(s"CFG saved to: $outputPath")
        } else {
          println(s"✗ No CFG generated for method: $methodName")
        }
      } 
      // generating DDG
        if (cpg.method.name(methodName).size > 0) {
        val outputFile = s"$outputPath/ddg/Sample.java.dot"
  //Generate DDG graph
        val dotDdg = cpg.method(methodName).dotDdg
            if (dotDdg.nonEmpty) {
                val file = new java.io.File(outputFile)
                val writer = new java.io.PrintWriter(file)
                writer.write(dotDdg.head)
                writer.close()
                println(s"DDGsaved to: $outputPath")
        } else {
          println(s"✗ No DDG generated for method: $methodName")
        }
      } 
    }
    
  } catch {
    case e: Exception => 
      println(s"✗ Error processing file $fileName: ${e.getMessage}")
      e.printStackTrace()
  } finally {
    try {
      println("done working")
    } catch {
      case _: Exception => // Ignore
    }
    
    // Clean up CPG
    try {
      cpg.close()
    } catch {
      case _: Exception => // Ignore
    }
  }
}

