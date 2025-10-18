public class Sample {
	public void searchProducts(String keyword) {
        Connection conn = null;
        Statement stmt = null;

        try {
            conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/testdb", "root", "password");
            stmt = conn.createStatement();

            
            String query = "SELECT * FROM products WHERE name LIKE '%" + keyword + "%'";
            ResultSet rs = stmt.executeQuery(query);

            while (rs.next()) {
                System.out.println("Product: " + rs.getString("name"));
            }

        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            try { if (stmt != null) stmt.close(); } catch (Exception e) {}
            try { if (conn != null) conn.close(); } catch (Exception e) {}
        }
    }
	}