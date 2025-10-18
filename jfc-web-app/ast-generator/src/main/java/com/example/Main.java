package com.example;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.printer.DotPrinter;
import com.github.javaparser.utils.Pair;

import java.io.*;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;



import static java.lang.Math.max;

public class Main {
   
    static void generateSingleDotFile(String inputFilePath, String outputDotPath) {
        try {
            File inputFile = new File(inputFilePath);
            
            // Check if input file exists and is a Java file
            if (!inputFile.exists()) {
                System.err.println("Input file does not exist: " + inputFilePath);
            
            }
            
            if (!inputFilePath.endsWith(".java")) {
                System.err.println("Input file must be a .java file: " + inputFilePath);
               
            }
            
            // Parse the Java file
            CompilationUnit cu = StaticJavaParser.parse(inputFile);
            
            // Create DOT printer
            DotPrinter printer = new DotPrinter(true);
            
            // Ensure output directory exists
            File outputFile = new File(outputDotPath + ".dot");
            File outputDir = outputFile.getParentFile();
            if (outputDir != null && !outputDir.exists()) {
                outputDir.mkdirs();
            }
            
            // Write DOT file
            try (FileWriter fileWriter = new FileWriter(outputFile);
                 PrintWriter printWriter = new PrintWriter(fileWriter)) {
                printWriter.print(printer.output(cu));
            }
            
            System.out.println("Successfully generated DOT file: " + outputFile.getAbsolutePath());
           // return true;
            
        } catch (Exception e) {
            System.err.println("Error parsing file: " + inputFilePath);
            System.err.println("Error message: " + e.getMessage());
            e.printStackTrace();
           
        }
    }
    static void generateSingleGraphData(String dotFilePath, String outputTxtPath) {
        try {
            File dotFile = new File(dotFilePath);
            
            if (!dotFile.exists()) {
                System.err.println("DOT file does not exist: " + dotFilePath);
            }
            
            int MAX_VEX_NUMBER = 0;
            ArrayList<Pair<Integer, Integer>> parseResult = new ArrayList<>();
            
            try (BufferedReader br = new BufferedReader(new FileReader(dotFile))) {
                String line;
                while ((line = br.readLine()) != null) {
                    if (checkIsGraphPath(line)) {
                        Pair<Integer, Integer> UV = parseGraphPath(line);
                        parseResult.add(UV);
                        MAX_VEX_NUMBER = max(MAX_VEX_NUMBER, max(UV.a, UV.b));
                    }
                }
            }
            
            // Ensure output directory exists
            File outputFile = new File(outputTxtPath);
            File outputDir = outputFile.getParentFile();
            if (outputDir != null && !outputDir.exists()) {
                outputDir.mkdirs();
            }
            
            // Save edge list
            try (BufferedWriter out = new BufferedWriter(new FileWriter(outputFile))) {
                for (Pair<Integer, Integer> item : parseResult) {
                    out.write(String.format("%d,%d\n", item.a, item.b));
                }
            }
            
            System.out.println("Successfully generated graph data: " + outputFile.getAbsolutePath());
          
            
        } catch (IOException e) {
            System.err.println("Error processing DOT file: " + dotFilePath);
            e.printStackTrace();
          
        }
    }

   

   

    static int[][] transMatrix(ArrayList<Pair<Integer, Integer>> parseResult, int MAX_VEX_NUMBER) {
        int[][] arc = new int[MAX_VEX_NUMBER][MAX_VEX_NUMBER];
        for (Pair<Integer, Integer> item : parseResult) {
            arc[item.a][item.b] = 1;
        }
        return arc;
    }

    static boolean checkIsGraphPath(String str) {
        Pattern pattern = Pattern.compile("^n(.*)->(.*);");
        Matcher match = pattern.matcher(str);
        return match.matches();
    }

    static Pair<Integer, Integer> parseGraphPath(String str) {
        Matcher matcher = Pattern.compile("[0-9]+").matcher(str);
        int matcher_start = 0;
        int first = 1, result1 = -1, result2 = -1;
        while (matcher.find(matcher_start)) {
            if (first == 1) {
                first = 0;
                result1 = Integer.parseInt(matcher.group(0));
            } else {
                result2 = Integer.parseInt(matcher.group(0));
            }
            matcher_start = matcher.end();
        }
        return new Pair<>(result1, result2);
    }

   
    

   
    public static void main( String[] args ) {
      
      String inputFile = args[0];
      String outputDotPath = args[1];
      
      generateSingleDotFile(inputFile, outputDotPath);
    
      generateSingleGraphData(outputDotPath + ".dot", outputDotPath + ".dot" + ".txt");

      
      
      
      
      
    }
}
