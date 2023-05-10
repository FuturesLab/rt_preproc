#include <stdio.h>

void func(){
  printf("foo");
}

void func2(){
  printf("bar");
}

int main(){
  if(FOO)
    func();

  #ifdef FOO
    func();
  #endif
  return 0;
}
