#include <stdio.h>      /* printf */

#ifdef FOO
  int var = 3;
#endif 
 
int main(){
  int x = 0;
  x = var + 1 + 1;
  printf("%d", x);
}
