#include <stdio.h>      /* printf */
#include <stdlib.h>     /* strtol */
#include <assert.h>     /* assert */

#define UNDEFINED_INT 0xdeadbeef

int FOO = UNDEFINED_INT;

int setup_env_vars() {
  // FOO
  char* foo_str = getenv("FOO");
  if (foo_str) {
    FOO = strtol(foo_str, NULL, 10);
  } else {
    fprintf(stderr, "Error: environment variable FOO not set\n");
  }
  return 0;
}

int func(){
  return 2;
}

int main(){
  if (setup_env_vars() != 0) {
    printf("Error setting up environment variables\n");
    return 1;
  }
  int fn_val = 0;
  if (FOO != UNDEFINED_INT) {
    fn_val = func();
  }
  printf("Result: %d\n", fn_val);
  return 0;
}