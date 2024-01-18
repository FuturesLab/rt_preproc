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

int val = 10;
char val_2 = 'a';

void func_1(int x){ 
    assert(FOO != UNDEFINED_INT);
    printf("FOO defined func! %d", x);
}
void func_2(char x){ 
    assert(FOO == UNDEFINED_INT);
    printf("FOO not defined func! %c", x);
}

int main(){
  setup_env_vars();
  if (FOO != UNDEFINED_INT) {
    func_1(val);
  }
  else {
    func_2(val_2);
  }
}
