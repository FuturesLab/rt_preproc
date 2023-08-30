#include <stdio.h>      /* printf */
#include <stdlib.h>     /* strtol */
#include <assert.h>     /* assert */
int func(){
  return 2;
}

int main(){
  int fn_val = 0;
  #ifdef FOO
    fn_val = func();
  #endif
  printf("Result: %d\n", fn_val);
  return 0;
}
