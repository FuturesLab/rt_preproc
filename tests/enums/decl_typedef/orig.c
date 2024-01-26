#include <stdio.h>      /* printf */

enum State {
  A,
  #ifdef FOO
    B,
  #endif
  C
};

typedef enum State State

int main(){
  State s = A;
  #ifdef FOO
    s = B;
  #endif
  printf("%d", s);
}
