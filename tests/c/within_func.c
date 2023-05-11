#include <stdio.h>

void foo(){
  printf("foo");
}

void bar(){
  printf("bar");
}

int main(){
  #ifdef FOO
    foo();
  #endif
  #ifdef BAR
    bar();
  #endif
  return 0;
}
