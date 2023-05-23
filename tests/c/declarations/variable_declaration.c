#include <stdio.h>

int main() {
  int x;
  #ifdef FOO
    int y = 2;
    int j = 3;
    x = y;
  #endif
  return x;
}