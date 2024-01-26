#include <stdio.h>      /* printf */

enum State {
  A,
  #ifdef FOO
    B,
  #endif
  C
};

int main(){
  enum State s = A;
  #ifdef FOO
    s = B;
  #endif
  printf("%d", s);
}
