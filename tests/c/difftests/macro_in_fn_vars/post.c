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

void func(int x){
  printf("Running FOO: %d\n", x);
  return;
}

int main(){
  if (setup_env_vars() != 0) {
    printf("Error setting up environment variables\n");
    return 1;
  }
  int x = UNDEFINED_INT;
  if (FOO != UNDEFINED_INT) {
    x = 2;
  }
  if (FOO != UNDEFINED_INT) {
    assert(x != UNDEFINED_INT);
    func(x);
  }
}
