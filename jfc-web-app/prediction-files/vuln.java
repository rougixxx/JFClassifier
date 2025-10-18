import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;

public class vuln {
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

    public void processUnsafeUserHitcountUpdates() throws Throwable {
        String data = badSource();

        if (data != null) {
            String names[] = data.split("-");
            int successCount = 0;
            Connection dbConnection = null;
            Statement sqlStatement = null;
            try {
                dbConnection = IO.getDBConnection();
                sqlStatement = dbConnection.createStatement();
                for (int i = 0; i < names.length; i++) {
                    
                    sqlStatement.addBatch("update users set hitcount=hitcount+1 where name='" + names[i] + "'");
                }
                int resultsArray[] = sqlStatement.executeBatch();
                for (int i = 0; i < names.length; i++) {
                    if (resultsArray[i] > 0) {
                        successCount++;
                    }
                }
                IO.writeLine("Succeeded in " + successCount + " out of " + names.length + " queries.");
            }
            catch (SQLException exceptSql) {
                IO.logger.log(Level.WARNING, "Error getting database connection", exceptSql);
            }
            finally {
                try {
                    if (sqlStatement != null) {
                        sqlStatement.close();
                    }
                }
                catch (SQLException exceptSql) {
                    IO.logger.log(Level.WARNING, "Error closing Statament", exceptSql);
                }

                try {
                    if (dbConnection != null) {
                        dbConnection.close();
                    }
                }
                catch (SQLException exceptSql) {
                    IO.logger.log(Level.WARNING, "Error closing Connection", exceptSql);
                }
            }
        }

    }
 // cwe129
    public void demonstrateNullOrEmptyArrayAccessException() throws Throwable {
        int data = badSource();

        int array[] = null;

        
        if (data >= 0) {
            array = new int[data];
        }
        else {
            IO.writeLine("Array size is negative");
        }

        
        array[0] = 5;
        IO.writeLine(array[0]);

    }

    public void cwe_789() throws Throwable {
        int data;

        
        data = Integer.MAX_VALUE;

        badSink(data  );
    }
        public void func_59739() throws Throwable {
        long data;

        
        data = (new java.security.SecureRandom()).nextLong();

        
        long result = (long)(--data);

        IO.writeLine("result: " + result);

    }
// cwe 330
        @Override
public void weak_remmemberme_login(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html;charset=UTF-8");

        javax.servlet.http.Cookie[] theCookies = request.getCookies();

        String param = "noCookieValueSupplied";
        if (theCookies != null) {
            for (javax.servlet.http.Cookie theCookie : theCookies) {
                if (theCookie.getName().equals("BenchmarkTest00068")) {
                    param = java.net.URLDecoder.decode(theCookie.getValue(), "UTF-8");
                    break;
                }
            }
        }

        String bar;

        
        int num = 106;

        bar = (7 * 18) + num > 200 ? "This_should_always_happen" : param;

        double value = java.lang.Math.random();
        String rememberMeKey = Double.toString(value).substring(2); 

        String user = "Doug";
        String fullClassName = this.getClass().getName();
        String testCaseNumber =
                fullClassName.substring(
                        fullClassName.lastIndexOf('.') + 1 + "BenchmarkTest".length());
        user += testCaseNumber;

        String cookieName = "rememberMe" + testCaseNumber;

        boolean foundUser = false;
        javax.servlet.http.Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (int i = 0; !foundUser && i < cookies.length; i++) {
                javax.servlet.http.Cookie cookie = cookies[i];
                if (cookieName.equals(cookie.getName())) {
                    if (cookie.getValue().equals(request.getSession().getAttribute(cookieName))) {
                        foundUser = true;
                    }
                }
            }
        }

        if (foundUser) {
            response.getWriter().println("Welcome back: " + user + "<br/>");

        } else {
            javax.servlet.http.Cookie rememberMe =
                    new javax.servlet.http.Cookie(cookieName, rememberMeKey);
            rememberMe.setSecure(true);
            rememberMe.setHttpOnly(true);
            rememberMe.setDomain(new java.net.URL(request.getRequestURL().toString()).getHost());
            rememberMe.setPath(request.getRequestURI()); 
            
            request.getSession().setAttribute(cookieName, rememberMeKey);
            response.addCookie(rememberMe);
            response.getWriter()
                    .println(
                            user
                                    + " has been remembered with cookie: "
                                    + rememberMe.getName()
                                    + " whose value is: "
                                    + rememberMe.getValue()
                                    + "<br/>");
        }
        response.getWriter().println("Weak Randomness Test java.lang.Math.random() executed");
    }

}
