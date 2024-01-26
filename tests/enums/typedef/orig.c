#include <stdio.h>      /* printf */

typedef enum {
  A,
  #ifdef FOO
    B,
  #endif
  C
} State;

int main(){
  State s = A;
  #ifdef FOO
    s = B;
  #endif
  printf("%d", s);
}
