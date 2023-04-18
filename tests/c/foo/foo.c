#include <stdio.h>

void func(){
  printf("foo");
}

void func2(){
  printf("bar");
}

int main(){
  #ifdef FOO
    func();
  #endif
  #ifdef BAR
    func2();
  #endif
  return 0;
}

