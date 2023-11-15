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

void func_1(){ 
    assert(FOO != UNDEFINED_INT);
    printf("FOO defined func!"); 
}
void func_2(){ 
    assert(FOO == UNDEFINED_INT);
    printf("FOO not defined func!"); 
}

int main(){
  setup_env_vars();
  if (FOO != UNDEFINED_INT) {
    func_1();
  }
  else {
    func_2();
  }
}
