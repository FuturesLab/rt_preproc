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

void func(){ 
    assert(FOO != UNDEFINED_INT);
    printf("FOO defined func!"); 
}

int main(){
  setup_env_vars();
  func();
}
