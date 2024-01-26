#include <stdio.h>      /* printf */

typedef struct {
  int x;
  #ifdef FOO
    int y;
  #endif
} st1;

int main(){
  st1 s;
  s.x = 1;
  #ifdef FOO
    s.y = 2;
  #endif
  printf("%d ", s.x);
  #ifdef FOO
    printf("%d", s.y);
  #endif
}
