#include <stdio.h>      /* printf */

void func(int x){
  printf("Running FOO: %d\n", x);
  return;
}

int main(){
  #ifdef FOO
    #ifdef BAR
      int x = 2;
    #endif
  #endif
  #ifdef FOO
    #ifdef BAR
      func(x);
    #endif
  #endif
}
