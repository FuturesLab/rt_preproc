#include <stdio.h>      /* printf */

struct st1 {
  int x;
  #ifdef FOO
    int y;
  #endif
};

int main(){
  struct st1 s;
  s.x = 1;
  #ifdef FOO
    s.y = 2;
  #endif
  printf("%d ", s.x);
  #ifdef FOO
    printf("%d", s.y);
  #endif
}
