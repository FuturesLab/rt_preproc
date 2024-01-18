#include <stdio.h>      /* printf */

#ifdef FOO
  int var = 3;
#endif 
 
int main(){
  int x = 0;
  #ifdef FOO
    x = var + 1 + 1;
    printf("%d", x);
  #endif
  printf("Hello!");
}
