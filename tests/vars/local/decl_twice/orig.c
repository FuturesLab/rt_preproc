#include <stdio.h>      /* printf */

void func(int x){
  printf("Running FOO: %d\n", x);
  return;
}

int main(){
  #ifdef FOO
    int x = 2;
  #endif
  #ifndef FOO
    int x = 4;
  #endif
  func(x);
}
