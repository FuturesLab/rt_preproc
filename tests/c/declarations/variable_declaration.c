#include <stdio.h>

int foo(int x){
  return x+1;
}

int main() {
  #ifdef FOO
    int x = 2;
  #endif
}