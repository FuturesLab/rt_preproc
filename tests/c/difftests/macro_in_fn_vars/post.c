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

void func(int x){
  printf("Running FOO: %d\n", x);
  return;
}

int main(){
  if (setup_env_vars() != 0) {
    printf("Error setting up environment variables\n");
    return 1;
  }
  int x = POISON_INT;
  if (FOO) {
    x = 2;
  }
  if (FOO) {
    assert(x != POISON_INT);
    func(x);
  }
}
