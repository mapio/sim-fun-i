import java.util.Scanner;

public class TestRunner {
    public static void main(String[] args) throws Exception {
        Scanner s = new Scanner(System.in);
        System.out.println(Sum.sum(s.nextInt(), s.nextInt()));
    }
}
