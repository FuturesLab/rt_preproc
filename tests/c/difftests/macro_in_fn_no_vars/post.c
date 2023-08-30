#include <stdio.h>      /* printf */
#include <stdlib.h>     /* strtol */
#include <assert.h>     /* assert */

#define POISON_INT 0xdeadbeef
int FOO = POISON_INT;

int setup_env_vars() {
  // FOO
  char* foo_str = getenv("FOO");
  if (foo_str) {
    FOO = strtol(foo_str, NULL, 10);
  } else {
    printf("FOO not set\n");
    return 1;
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
  if (FOO) {
    fn_val = func();
  }
  printf("Result: %d\n", fn_val);
  return 0;
}