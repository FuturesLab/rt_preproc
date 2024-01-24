#include <stdio.h>      /* printf */

#ifdef FOO
  #define var 3
#else
  #define var 4
#endif
 
int main(){
  int x = var + 1;
  printf("%d", x);
}
