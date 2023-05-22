#include <stdio.h>

int main() {
  int x;
  #ifdef FOO
    int y = 2;
    x = y;
  #endif
  return x;
}