public class Sample {
	 static void saveEdge(ArrayList<Pair<Integer, Integer>> parseResult, String filePath, String fileName) throws IOException {
        System.out.println(filePath + "/" + fileName);
        BufferedWriter out = new BufferedWriter(new FileWriter(filePath + "/" + fileName));
        for (Pair<Integer, Integer> item : parseResult) {
            out.write(String.format("%d,%d\n", item.a, item.b));
        }
        out.close();
    }
	}