load test_helper

teardown() {
    rm -f *.class actual-*.txt errors-*.txt diffs-*.txt
}

@test "compiling 'empty' (missing source)" {
  cd $FIXTURES/empty
  run sf compile
  [ "$status" -eq 1 ]
  [[ ${lines[0]} =~ .*"No main source file found".* ]]
}

@test "compiling 'sum' (a correct program)" {
  cd $FIXTURES/java/sum
  run sf compile
  [ "$status" -eq 0 ]
  [[ ${lines[0]} =~ .*"Using processor: JavaSolution".* ]]
  [[ ${lines[1]} =~ .*"Succesfully compiled sources: Solution.java".* ]]
}

@test "compiling 'sum_mismatch' (public class, file/class name mismatch)" {
  cd $FIXTURES/java/sum_mismatch
  run sf compile
  [ "$status" -eq 1 ]
  [[ ${lines[2]} =~ .*"Nope.java:3: error: class Solution is public, should be declared in a file named Solution.java".* ]]
}

@test "compiling 'sum_nonpublic' (non public class)" {
  cd $FIXTURES/java/sum_nonpublic
  run sf compile
  [ "$status" -eq 0 ]
  [[ ${lines[0]} =~ .*"Using processor: JavaSolution".* ]]
  [[ ${lines[1]} =~ .*"Succesfully compiled sources: Solution.java".* ]]
}

@test "compiling 'sum_nomain' (public class, no main method)" {
  cd $FIXTURES/java/sum_nomain
  run sf compile
  [ "$status" -eq 1 ]
  [[ ${lines[0]} =~ .*"No main source file found".* ]]
}

@test "compiling 'sum_testrunner' (a correct program, with a TestRunner class)" {
  cd $FIXTURES/java/sum_testrunner
  run sf compile
  [ "$status" -eq 0 ]
  [[ ${lines[0]} =~ .*"Using processor: JavaTestRunnerSolution".* ]]
}

@test "generating 'sum' output" {
  cd $FIXTURES/java/sum
  run sf generate -f
  [ "$status" -eq 0 ]
  [ -r expected-1.txt ]
  [ -r expected-2.txt ]
  [ ! -r args-1.txt ]
  [ ! -r args-2.txt ]
  [[ ${lines[0]} =~ .*"Using processor: JavaSolution".* ]]
  [[ ${lines[1]} =~ .*"Succesfully compiled sources: Solution.java".* ]]
  [[ ${lines[2]} =~ .*"Generated expected output for cases: 1, 2".* ]]
}

@test "testing 'sum' output" {
  cd $FIXTURES/java/sum
  sf generate -f
  run sf test -f
  [ ! -r diffs-1.txt ]
  [ ! -r diffs-2.txt ]
  [ ! -r errors-1.txt ]
  [ ! -r errors-2.txt ]
  rm -f expected-*.txt
  [ "$status" -eq 0 ]
  [[ ${lines[0]} =~ .*"Using processor: JavaSolution".* ]]
  [[ ${lines[1]} =~ .*"Succesfully compiled sources: Solution.java".* ]]
  [[ ${lines[2]} =~ .*"Generated actual output for cases: 1, 2".* ]]
  [[ ${lines[3]} =~ .*"Cases run with no diffs or errors".* ]]
}

@test "testing 'sum_testrunner' output" {
  cd $FIXTURES/java/sum_testrunner
  run sf test -f
  [ ! -r diffs-1.txt ]
  [ ! -r diffs-2.txt ]
  [ ! -r errors-1.txt ]
  [ ! -r errors-2.txt ]
  [ "$status" -eq 0 ]
  [[ ${lines[0]} =~ .*"Using processor: JavaTestRunnerSolution".* ]]
  [[ ${lines[3]} =~ .*"Cases run with no diffs or errors".* ]]
}

@test "diffing 'sum_diff' differences" {
  cd $FIXTURES/java/sum_diffs
  run sf test -f
  [ -r diffs-1.txt ]
  [ -r diffs-2.txt ]
  [ ! -r errors-1.txt ]
  [ ! -r errors-2.txt ]
  [ "$status" -eq 0 ]
  [[ ${lines[0]} =~ .*"Using processor: JavaSolution".* ]]
  [[ ${lines[1]} =~ .*"Succesfully compiled sources: Solution.java".* ]]
  [[ ${lines[2]} =~ .*"Generated actual output for cases: 1, 2".* ]]
  [[ ${lines[3]} =~ .*"Case 1 returned the following diffs:".* ]]
  [[ ${lines[11]} =~ .*"Case 2 returned the following diffs:".* ]]
}
