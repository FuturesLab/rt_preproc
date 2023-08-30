#include <stdio.h>      /* printf */

void func(int x){
  printf("Running FOO: %d\n", x);
  return;
}

int main(){
  #ifdef FOO
    int x = 2;
  #endif
  #ifdef FOO
    func(x);
  #endif
}
