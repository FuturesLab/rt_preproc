#include <stdio.h>      /* printf */
#include <assert.h>     /* assert */

struct st1 {
  int x;
  #ifdef FOO
    int y;
  #endif
};

int main(){
  struct st1 s;
  #ifdef FOO
    assert(sizeof(s) == 2 * sizeof(int));
  #else
    assert(sizeof(s) == sizeof(int));
  #endif
  s.x = 1;
  #ifdef FOO
    s.y = 2;
  #endif
  printf("%d ", s.x);
  #ifdef FOO
    printf("%d", s.y);
  #endif
}
