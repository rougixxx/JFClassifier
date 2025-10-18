import better.files._
import io.shiftleft.semanticcpg.language._
import java.io.{File, PrintWriter, FileWriter, BufferedWriter}
import java.nio.file.{Files, Paths}

@main def generateCfgFromFiles(fileListPath: String, outputDir: String) = {

  // val folder = new File(javaFolderPath)
 //  val javaFiles = folder.listFiles.filter(_.isFile).filter(_.getName.endsWith(".java"))
  //  .map(_.getPath).toList
 //  val totalFiles = javaFiles.length

    // Read list of files to process from the batch file
  val fileLines = scala.io.Source.fromFile(fileListPath).getLines().toList
  val totalFiles = fileLines.length
  
    // Create failure log file
  val failedFilesLog = new File(s"$outputDir/failed_imports.txt")
  val failureWriter = new BufferedWriter(new FileWriter(failedFilesLog, true)) // Append mode
  println(s"Processing batch with $totalFiles files")
  // Iteration through java files
  fileLines.zipWithIndex.foreach { case (filePath, index) =>
    val fileName = new File(filePath).getName // returns Sample_number.java

    try {
      // Extract sample number for method name
      println(s"[${index+1}/$totalFiles] Processing: $fileName *******************************************")
      val sampleNumberRegex = """Sample_(\d+)(?:\.java)?""".r
      val methodName = fileName match {
        case sampleNumberRegex(number) => s"func_$number"
        case _ => "main" // Fallback to "main"
      }
      
      // Reset CPG for each file
      if (index > 0) {
        try {
          cpg.close()
        } catch {
          case _: Exception => // Ignore reset errors
        }
      }
      
     // Try multiple import approaches in sequence
      var importSucceeded = false
      
      // Approach 1: Standard import
      try {
        importCode.java(filePath)
        importSucceeded = true
      } catch {
        case e: Exception => 
          println(s"Standard import failed, trying with absolute path...")
      }
      
      // Approach 2: Absolute path
      if (!importSucceeded) {
        try {
          importCode(new File(filePath).getAbsolutePath)
          importSucceeded = true
        } catch {
          case e: Exception => 
            println(s"Absolute path import failed, trying with file content...")
        }
      }
      
      // Approach 3: From string
      if (!importSucceeded) {
        try {
          val fileContent = scala.io.Source.fromFile(filePath).mkString
          importCode.java.fromString(fileContent)
          importSucceeded = true
        } catch {
          case e: Exception => 
         
            println(s"All import attempts failed for $fileName: ${e.getMessage}")
            
            // Log failed file path to the failed_imports.txt file
            failureWriter.write(s"$filePath\n")
            failureWriter.write(s"Error: ${e.getMessage}\n\n")
            failureWriter.flush() // Make sure it's written immediately
            
            throw new Exception(s"Unable to import file: ${e.getMessage}")
        }
      }
      // Check if method exists
      if (cpg.method.name(methodName).size > 0) {
        val outputPath = s"$outputDir/$fileName.dot"
  //Generate CFG graph
        val dotCfg = cpg.method(methodName).dotCfg
            if (dotCfg.nonEmpty) {
                val file = new java.io.File(outputPath)
                val writer = new java.io.PrintWriter(file)
                writer.write(dotCfg.head)
                writer.close()
                println(s"CFG saved to: $outputPath")
        } else {
          println(s"✗ No CFG generated for method: $methodName")
        }
      } 

    } catch {
      case e: Exception => 
        println(s"✗ Error processing file $fileName: ${e.getMessage}")
    }
  }
  

}
// ✗ Error processing file Sample_24818.java: Error creating project for input path: `/home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/dataset/java-files/Sample_24818.java`