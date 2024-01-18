#include <stdio.h>      /* printf */
#include <stdlib.h>     /* malloc */

struct st1 {
  int x;
  #ifdef FOO
    int y;
  #endif
};

int main(){
  struct st1* s = malloc(sizeof(struct st1));
  s->x = 1;
  #ifdef FOO
    s->y = 2;
  #endif
  printf("%d ", s->x);
}
