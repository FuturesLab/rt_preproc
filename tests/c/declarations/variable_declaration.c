#include <stdio.h>

int main() {
  int x;
  #ifdef FOO
    x = 3;
    int y = 2;
    void foo();
    int j = 3;
    x = y;
  #endif
  return x;
}