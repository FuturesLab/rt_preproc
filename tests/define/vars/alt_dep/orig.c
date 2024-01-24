#include <stdio.h>      /* printf */

#ifdef FOO
  #define var 3
#else
  #define var 4
#endif

#define BAR (var + 1)
 
int main(){
  int x = BAR + 1;
  printf("%d", x);
}
