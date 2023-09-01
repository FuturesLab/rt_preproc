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
  }
  return 0;
}

int func_1(int val) {
  assert(FOO != UNDEFINED_INT);
  return val + 1;
}

char func_2(char val) {
  assert(FOO == UNDEFINED_INT);
  return val;
}

int main(){
  setup_env_vars();
  int x_int;
  char x_char;
  if (FOO != UNDEFINED_INT) {
    x_int = func_1(3);
  } else {
    x_char = func_2(3);
  }
  if (FOO != UNDEFINED_INT) {
    printf("%d", func_1(3));
  } else {
    printf("%c", func_2(3));
  }
}
